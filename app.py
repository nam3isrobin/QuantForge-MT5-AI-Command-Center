import streamlit as st
import pandas as pd
import os
from datetime import datetime

import config
from services.mt5_cli_runner import run_mt5_cli_backtest
import database.db as db
from services.settings_manager import load_settings, save_settings
from services.mt5_parser import parse_mt5_html_cached, parse_ea_inputs, extract_all_metrics
from services.ui_renderer import inject_custom_css, render_metrics_grid, render_interactive_curve, render_ai_analysis

# Configure Streamlit page
st.set_page_config(page_title="QuantForge", page_icon="⚡", layout="wide")

def main():
    inject_custom_css()
    db.init_db()
    
    st.markdown('''
        <div class="glass-header">
            <h1><span class="emoji">⚡</span> QuantForge: MT5 AI Command Center</h1>
        </div>
    ''', unsafe_allow_html=True)
    
    st.sidebar.header("🤖 1. Expert Advisor")
    uploaded_ex5 = st.sidebar.file_uploader("Upload an Expert Advisor (.ex5)", type=['ex5'])
    
    ex5_path = None
    ea_name = None
    if uploaded_ex5:
        ea_name = uploaded_ex5.name
        ex5_path = os.path.join(config.STRATEGIES_DIR, ea_name)
        with open(ex5_path, "wb") as f:
            f.write(uploaded_ex5.getbuffer())
        st.sidebar.success(f"Loaded: {ea_name}")
    
    st.sidebar.header("⚙️ 2. Global Configuration")
    col1, col2 = st.sidebar.columns(2)
    start_date = col1.date_input("Start Date", datetime(2023, 1, 1))
    end_date = col2.date_input("End Date", datetime(2023, 12, 31))
    initial_balance = st.sidebar.number_input("Deposit ($)", min_value=100.0, value=config.DEFAULT_CAPITAL)
    leverage = st.sidebar.number_input("Leverage (1:X)", min_value=1, value=100)
    
    current_risk = st.session_state.get('risk_percent_slider', 2.0)
    risk_money = (current_risk / 100.0) * initial_balance
    
    risk_percent = st.sidebar.slider(
        f"Risk per Trade [%] (${risk_money:.2f})", 
        min_value=0.1, max_value=20.0, value=2.0, step=0.1,
        key='risk_percent_slider'
    )
    
    st.sidebar.markdown("---")
    st.sidebar.header("⏱️ 3. Trading Filter")
    
    SESSION_MAP = {
        "🌍 24/7 (All Sessions)": "0-23",
        "🦘 Sydney (17:00 - 02:00)": "17-2",
        "🗼 Tokyo (19:00 - 04:00)": "19-4",
        "💂 London (03:00 - 12:00)": "3-12",
        "🗽 New York (08:00 - 17:00)": "8-17",
        "🔥 Golden Overlap (08:00 - 12:00)": "8-12"
    }
    
    selected_sessions = st.sidebar.multiselect(
        "Trading Sessions (EST)",
        options=list(SESSION_MAP.keys()),
        default=["🌍 24/7 (All Sessions)"],
        help="Select one or multiple sessions to trade. Selecting 24/7 overrides others."
    )
    
    trading_hours_str = "0-23"
    if selected_sessions:
        if "🌍 24/7 (All Sessions)" in selected_sessions:
            trading_hours_str = "0-23"
        else:
            trading_hours_str = ",".join([SESSION_MAP[s] for s in selected_sessions])
            
    st.sidebar.markdown("---")
    st.sidebar.header("🎛️ 4. Input Parameters")
    default_inputs = "InpFastMA=10\nInpSlowMA=20\nInpStopLossPips=50" if ea_name == "MACross.ex5" else ""
    raw_inputs = st.sidebar.text_area("Inputs", value=default_inputs, height=120)
    ea_inputs = parse_ea_inputs(raw_inputs)
    
    ea_inputs["InpRiskPercentage"] = str(risk_percent)
    ea_inputs["InpTradingHours"] = trading_hours_str
    
    st.sidebar.markdown("---")
    st.sidebar.header("🧠 5. AI Analyst")
    
    settings = load_settings()
    saved_api_key = settings.get("gemini_api_key", "")
    saved_model = settings.get("gemini_model_name", "")
    
    gemini_api_key = st.sidebar.text_input("Gemini API Key", value=saved_api_key, type="password", help="Get a free key from Google AI Studio to use the AI Strategy Analyst.")
    
    if saved_api_key:
        if st.sidebar.button("🗑️ Clear Saved Key"):
            settings["gemini_api_key"] = ""
            settings["gemini_model_name"] = ""
            save_settings(settings)
            st.rerun()
            
    if gemini_api_key:
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            default_index = 0
            if saved_model in available_models:
                default_index = available_models.index(saved_model)
            else:
                for i, m in enumerate(available_models):
                    if 'gemini-1.5-pro' in m.lower():
                        default_index = i
                        break
                    elif 'gemini-1.5-flash' in m.lower():
                        default_index = i
            
            selected_model = st.sidebar.selectbox("Select AI Model", available_models, index=default_index)
            st.session_state['gemini_model_name'] = selected_model
            
            if gemini_api_key != saved_api_key or selected_model != saved_model:
                settings["gemini_api_key"] = gemini_api_key
                settings["gemini_model_name"] = selected_model
                save_settings(settings)
                
        except Exception as e:
            st.sidebar.error(f"Error fetching models: {e}")
            st.session_state['gemini_model_name'] = 'gemini-1.5-pro'
    else:
        if saved_api_key != "":
            settings["gemini_api_key"] = ""
            save_settings(settings)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Single Backtest", 
        "📚 Batch Testing", 
        "📜 History Ledger",
        "🚀 Live Deploy"
    ])
    
    with tab1:
        st.header("🎯 Single Symbol Backtest")
        st.divider()
        symbol = st.selectbox("Symbol", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"])
        timeframe = st.selectbox("Timeframe", ["M1", "M5", "M15", "H1", "H4", "D1"])
        
        if not ex5_path:
            st.info("👈 Please upload an `.ex5` Expert Advisor file to begin.")
        else:
            if st.button("🚀 Run Native MT5 Backtest"):
                with st.spinner("Running MT5 Strategy Tester..."):
                    try:
                        report_path = run_mt5_cli_backtest(
                            ex5_path=ex5_path, symbol=symbol, timeframe=timeframe,
                            start_date=start_date, end_date=end_date,
                            initial_deposit=initial_balance, leverage=leverage,
                            ea_inputs=ea_inputs
                        )
                        st.session_state['single_report_path'] = report_path
                        
                        tables = parse_mt5_html_cached(report_path)
                        if tables:
                            metrics = extract_all_metrics(tables[0])
                            db.save_backtest_result(ea_name, symbol, timeframe, start_date, end_date, ea_inputs, metrics, report_path)
                            st.success("Results saved to History Ledger!")
                            
                    except Exception as e:
                        st.error(f"Error running backtest: {e}")
                        
            if 'single_report_path' in st.session_state and os.path.exists(st.session_state['single_report_path']):
                report_path = st.session_state['single_report_path']
                
                try:
                    with st.spinner("Parsing MT5 Data for Interactive Graphs..."):
                        tables = parse_mt5_html_cached(report_path)
                        
                    if tables:
                        st.header("📊 Native Strategy Results")
                        st.divider()
                        metrics = extract_all_metrics(tables[0])
                        render_metrics_grid(metrics)
                        render_interactive_curve(tables, key="single_backtest_chart")
                        render_ai_analysis(metrics, gemini_api_key)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        report_filename = os.path.basename(report_path)
                        report_url = f"app/static/reports/{report_filename}"
                        st.link_button("🔗 Open Full MT5 Report with Scatter Plots in Browser", report_url, type="primary")
                except Exception as parse_e:
                    st.warning(f"Could not parse the report natively: {parse_e}")
                    
    with tab2:
        st.header("📚 Batch Testing (Multiple Symbols)")
        st.divider()
        batch_symbols = st.multiselect("Select Symbols to Batch Test", config.DEFAULT_SYMBOLS, default=["EURUSD", "GBPUSD"])
        batch_timeframe = st.selectbox("Batch Timeframe", ["M1", "M5", "M15", "H1", "H4", "D1"], key="batch_tf")
        
        if not ex5_path:
            st.info("👈 Please upload an `.ex5` Expert Advisor file to begin.")
        elif not batch_symbols:
            st.warning("Please select at least one symbol.")
        else:
            if st.button("📚 Run Batch Backtest"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                batch_results = []
                st.session_state['batch_reports'] = []
                
                import concurrent.futures
                
                def run_single_batch(sym):
                    try:
                        report_path = run_mt5_cli_backtest(
                            ex5_path=ex5_path, symbol=sym, timeframe=batch_timeframe,
                            start_date=start_date, end_date=end_date,
                            initial_deposit=initial_balance, leverage=leverage,
                            ea_inputs=ea_inputs
                        )
                        tables = parse_mt5_html_cached(report_path)
                        if tables:
                            metrics = extract_all_metrics(tables[0])
                            db.save_backtest_result(ea_name, sym, batch_timeframe, start_date, end_date, ea_inputs, metrics, report_path)
                            
                            return {
                                "success": True,
                                "symbol": sym,
                                "report_path": report_path,
                                "metrics": metrics
                            }
                    except Exception as e:
                        return {"success": False, "symbol": sym, "error": str(e)}
                    return {"success": False, "symbol": sym, "error": "Unknown error parsing tables."}

                status_text.text(f"Dispatching {len(batch_symbols)} MT5 headless instances sequentially...")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    futures = {executor.submit(run_single_batch, sym): sym for sym in batch_symbols}
                    
                    completed_count = 0
                    for future in concurrent.futures.as_completed(futures):
                        res = future.result()
                        completed_count += 1
                        progress_bar.progress(completed_count / len(batch_symbols))
                        
                        sym = res['symbol']
                        if res['success']:
                            status_text.text(f"Completed {sym} ({completed_count}/{len(batch_symbols)})")
                            m = res['metrics']
                            batch_results.append({
                                "Symbol": sym,
                                "Net Profit": m.get("Total Net Profit", 0),
                                "Trades": m.get("Total Trades", 0),
                                "Drawdown": m.get("Max Drawdown", 0),
                                "Win Rate": m.get("Win Rate", "0%")
                            })
                            st.session_state['batch_reports'].append({
                                "symbol": sym,
                                "report_path": res['report_path']
                            })
                        else:
                            st.error(f"Error running backtest for {sym}: {res.get('error')}")
                
                status_text.success("Batch Testing Complete! All results saved to History Ledger.")
                
                if batch_results:
                    st.header("📈 Batch Portfolio Summary")
                    st.divider()
                    batch_df = pd.DataFrame(batch_results)
                    st.dataframe(batch_df, use_container_width=True)
            
            if 'batch_reports' in st.session_state and st.session_state['batch_reports']:
                st.header("🔍 Detailed Batch Results")
                st.divider()
                for result in st.session_state['batch_reports']:
                    with st.expander(f"📊 Results for {result['symbol']}"):
                        report_path = result['report_path']
                        if os.path.exists(report_path):
                            try:
                                tables = parse_mt5_html_cached(report_path)
                                if tables:
                                    metrics = extract_all_metrics(tables[0])
                                    render_metrics_grid(metrics)
                                    render_interactive_curve(tables, key=f"batch_chart_{result['symbol']}")
                                    render_ai_analysis(metrics, gemini_api_key)
                                    
                                    st.markdown("<br>", unsafe_allow_html=True)
                                    report_filename = os.path.basename(report_path)
                                    report_url = f"app/static/reports/{report_filename}"
                                    st.link_button(f"🔗 Open Full MT5 Report for {result['symbol']} in Browser", report_url, type="primary")
                            except Exception as parse_e:
                                st.warning(f"Could not parse the report natively: {parse_e}")
                        else:
                            st.error("Report file not found.")
    with tab3:
        st.header("📜 History Ledger")
        st.divider()
        history = db.get_all_backtests()
        if history:
            df_hist = pd.DataFrame(history)
            display_df = df_hist.drop(columns=['inputs_json', 'report_path', 'id'])
            st.dataframe(display_df, use_container_width=True)
            
            csv = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Ledger to CSV",
                data=csv,
                file_name="mt5_history_ledger.csv",
                mime="text/csv",
                type="primary"
            )
            
            st.markdown("---")
            st.header("🔍 Detailed Report Viewer")
            st.divider()
            hist_options = {f"[{row['timestamp']}] {row['symbol']} ({row['timeframe']}) - Profit: ${row['net_profit']}": row for row in history}
            selected_hist = st.selectbox("Select a Backtest Run to load its interactive UI", options=["-- Select a Run --"] + list(hist_options.keys()))
            
            if selected_hist != "-- Select a Run --":
                selected_row = hist_options[selected_hist]
                hist_report_path = selected_row['report_path']
                
                col_view, col_del = st.columns([4, 1])
                with col_del:
                    if st.button("🗑️ Delete Record", key=f"del_{selected_row['id']}"):
                        db.delete_backtest(selected_row['id'])
                        st.success("Record deleted! Refreshing...")
                        st.rerun()
                        
                if os.path.exists(hist_report_path):
                    try:
                        with st.spinner("Parsing Historical MT5 Data..."):
                            tables = parse_mt5_html_cached(hist_report_path)
                        
                        if tables:
                            metrics = extract_all_metrics(tables[0])
                            render_metrics_grid(metrics)
                            render_interactive_curve(tables, key=f"history_chart_{selected_hist}")
                            render_ai_analysis(metrics, gemini_api_key)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            report_filename = os.path.basename(hist_report_path)
                            report_url = f"app/static/reports/{report_filename}"
                            st.link_button("🔗 Open Full Historical MT5 Report in Browser", report_url, type="primary")
                    except Exception as e:
                        st.error(f"Error parsing historical report: {e}")
                else:
                    st.error("Report file not found on disk. It may have been deleted.")
                    
            st.markdown("---")
            if st.button("🚨 Clear Entire History Ledger", type="primary"):
                db.clear_all_backtests()
                st.success("Ledger cleared! Refreshing...")
                st.rerun()
        else:
            st.info("No backtests have been run yet.")
            
    with tab4:
        st.header("🚀 Live Deployment Packager")
        st.divider()
        st.info("Package your Expert Advisor and optimized SET files for deployment on a VPS.")
        
        if not ex5_path:
            st.warning("👈 Please upload an `.ex5` Expert Advisor file first.")
        else:
            st.write("Clicking below will generate a `.set` file with your current inputs and package it alongside the EA into a deployable ZIP.")
            
            if st.button("📦 Generate Deployment Package"):
                import zipfile
                import io
                
                set_content = ""
                for k, v in ea_inputs.items():
                    set_content += f"{k}={v}\n"
                    
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.write(ex5_path, arcname=f"MQL5/Experts/{ea_name}")
                    zf.writestr(f"MQL5/Presets/{ea_name.replace('.ex5', '')}_Optimized.set", set_content)
                    
                    readme_content = f"Deployment Instructions for {ea_name}:\n\n1. Extract this ZIP into your MetaTrader 5 Data Folder.\n2. Open MT5, refresh your Navigator panel.\n3. Drag {ea_name} onto a chart.\n4. Click 'Load' and select the Preset file located in MQL5/Presets/.\n5. Enable AutoTrading!"
                    zf.writestr("README.txt", readme_content)
                
                st.download_button(
                    label="⬇️ Download Deployment ZIP",
                    data=zip_buffer.getvalue(),
                    file_name=f"{ea_name.replace('.ex5', '')}_Deployment.zip",
                    mime="application/zip",
                    type="primary"
                )
                st.success("Deployment Package generated successfully!")

if __name__ == "__main__":
    main()
