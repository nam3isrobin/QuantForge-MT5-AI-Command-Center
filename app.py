import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import base64
import webbrowser
import re

import config
from services.mt5_cli_runner import run_mt5_cli_backtest
import database.db as db

# Persistent settings handling
SETTINGS_FILE = os.path.join(config.BASE_DIR, "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

# Configure Streamlit page
st.set_page_config(page_title="QuantForge", page_icon="⚡", layout="wide")

# Inject Premium UI CSS & Fix Emoji Rendering Bug in Chromium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Fix the white emoji bug caused by Streamlit's webkit text fill */
    h1, h2, h3, h4, h5, h6, .st-emotion-cache-10trblm {
        -webkit-text-fill-color: initial !important;
        color: #ffffff !important;
    }
    
    /* Animated Gradient Background */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #020617, #172554) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 15s ease infinite !important;
        color: #f1f5f9;
    }
    
    /* Glassmorphic Sticky Header */
    .glass-header {
        position: sticky;
        top: 2rem;
        z-index: 999;
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        border-radius: 24px;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
        text-align: center;
    }
    .glass-header h1 {
        margin: 0 !important;
        padding: 0 !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent !important; 
    }
    .glass-header .emoji {
        -webkit-text-fill-color: initial !important;
        margin-right: 10px;
    }
    
    /* Glassmorphic Tabs */
    div[data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 8px !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    div[data-baseweb="tab-panel"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        margin-top: 1rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Make dividers look more premium */
    hr {
        margin-top: 0.5rem !important;
        margin-bottom: 1.5rem !important;
        border-color: rgba(255,255,255,0.1) !important;
    }
    
    /* Glassmorphic Container for Metrics */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    /* Metric Text Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Hover effects */
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(59, 130, 246, 0.2);
        border: 1px solid rgba(59, 130, 246, 0.4);
    }
    
    /* Glass Buttons & Inputs */
    div.stButton > button, a[data-testid="stLinkButton"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover, a[data-testid="stLinkButton"]:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.5) !important;
    }
    
    /* Dataframe Glassmorphism */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def parse_mt5_html_cached(report_path):
    import pandas as pd
    return pd.read_html(report_path, encoding='utf-16')

import re

def parse_optimization_xml(file_path):
    try:
        with open(file_path, "r", encoding="utf-16") as f:
            content = f.read()
    except (UnicodeError, FileNotFoundError):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
    row_pattern = re.compile(r'<Row.*?>(.*?)</Row>', re.DOTALL | re.IGNORECASE)
    cell_pattern = re.compile(r'<Data.*?>(.*?)</Data>', re.DOTALL | re.IGNORECASE)
    
    rows = row_pattern.findall(content)
    if not rows:
        return pd.DataFrame()
        
    data = []
    headers = []
    
    for i, row in enumerate(rows):
        cells = cell_pattern.findall(row)
        clean_cells = [c.strip() for c in cells]
        
        if i == 0:
            headers = clean_cells
        else:
            if len(clean_cells) == len(headers):
                data.append(clean_cells)
                
    df = pd.DataFrame(data, columns=headers)
    
    # Convert numeric columns where possible
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass
        
    return df

def extract_metric(df, metric_name):
    for i in range(len(df)):
        for j in range(len(df.columns) - 1):
            if str(df.iloc[i, j]).strip() == metric_name:
                for k in range(j+1, len(df.columns)):
                    val = str(df.iloc[i, k]).strip()
                    if val != metric_name and val != 'nan':
                        return val
    return "N/A"

def extract_all_metrics(df):
    keys = [
        "Total Net Profit:", "Gross Profit:", "Gross Loss:", "Profit Factor:",
        "Total Trades:", "Expected Payoff:", "Sharpe Ratio:", "Equity Drawdown Maximal:",
        "Profit Trades (% of total):", "Recovery Factor:", "History Quality:", "Maximal consecutive profit (count):"
    ]
    metrics = {}
    for k in keys:
        clean_key = k.replace(":", "").replace("Equity Drawdown Maximal", "Max Drawdown").replace("Profit Trades (% of total)", "Win Rate").replace("Maximal consecutive profit (count)", "Max Cons. Wins")
        metrics[clean_key] = extract_metric(df, k)
        
    try:
        net_profit = float(str(metrics.get("Total Net Profit", "0")).replace(' ', ''))
        max_dd_str = str(metrics.get("Max Drawdown", "0"))
        max_dd = float(max_dd_str.split('(')[0].replace(' ', '')) if '(' in max_dd_str else float(max_dd_str.replace(' ', ''))
        metrics['Calmar Ratio (Est)'] = f"{net_profit / max_dd:.2f}" if max_dd > 0 else "N/A"
    except:
        metrics['Calmar Ratio (Est)'] = "N/A"
        
    return metrics

def render_metrics_grid(metrics):
    st.write("#### Profitability")
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Total Net Profit", metrics.get("Total Net Profit", "N/A"))
    mc2.metric("Gross Profit", metrics.get("Gross Profit", "N/A"))
    mc3.metric("Gross Loss", metrics.get("Gross Loss", "N/A"))
    mc4.metric("Profit Factor", metrics.get("Profit Factor", "N/A"))
    
    st.write("#### Performance Stats")
    mc5, mc6, mc7, mc8 = st.columns(4)
    mc5.metric("Total Trades", metrics.get("Total Trades", "N/A"))
    mc6.metric("Expected Payoff", metrics.get("Expected Payoff", "N/A"))
    mc7.metric("Sharpe Ratio", metrics.get("Sharpe Ratio", "N/A"))
    mc8.metric("Max Drawdown", metrics.get("Max Drawdown", "N/A"))
    
    st.write("#### Advanced Ratios")
    mc9, mc10, mc11, mc12 = st.columns(4)
    mc9.metric("Win Rate", metrics.get("Win Rate", "N/A"))
    mc10.metric("Recovery Factor", metrics.get("Recovery Factor", "N/A"))
    mc11.metric("Calmar Ratio (Est)", metrics.get("Calmar Ratio (Est)", "N/A"))
    mc12.metric("Max Cons. Wins", metrics.get("Max Cons. Wins", "N/A"))

def render_interactive_curve(tables, key=None):
    if len(tables) > 1:
        st.markdown("---")
        st.write("### Interactive Equity Curve")
        df = tables[1]
        
        deals_idx_list = df[df[0] == 'Deals'].index
        if len(deals_idx_list) > 0:
            deals_idx = deals_idx_list[0]
            deals_df = df.iloc[deals_idx+2:].copy()
            deals_df.columns = df.iloc[deals_idx+1]
            
            if 'Balance' in deals_df.columns and 'Time' in deals_df.columns:
                deals_df['Balance'] = deals_df['Balance'].astype(str).str.replace(' ', '')
                deals_df['Balance'] = pd.to_numeric(deals_df['Balance'], errors='coerce')
                deals_df = deals_df.dropna(subset=['Balance'])
                
                if not deals_df.empty:
                    deals_df['Trade Number'] = range(1, len(deals_df) + 1)
                    deals_df['Peak'] = deals_df['Balance'].cummax()
                    deals_df['Drawdown'] = (deals_df['Peak'] - deals_df['Balance']) / deals_df['Peak'] * 100
                    
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    fig.add_trace(
                        go.Scatter(
                            x=deals_df['Trade Number'],
                            y=deals_df['Balance'],
                            name="Balance",
                            fill='tozeroy',
                            fillcolor='rgba(139, 92, 246, 0.2)',
                            line=dict(color='#8b5cf6', width=2),
                            hovertemplate="<b>Trade: %{x}</b><br>Balance: $%{y:,.2f}<extra></extra>"
                        ),
                        secondary_y=False
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=deals_df['Trade Number'],
                            y=deals_df['Drawdown'],
                            name="Drawdown (%)",
                            fill='tozeroy',
                            fillcolor='rgba(239, 68, 68, 0.1)',
                            line=dict(color='#ef4444', width=1),
                            hovertemplate="Drawdown: %{y:.2f}%<extra></extra>"
                        ),
                        secondary_y=True
                    )
                    
                    max_dd = deals_df['Drawdown'].max()
                    y2_range = [max_dd * 1.5 if max_dd > 0 else 10, 0] # Hang from top
                    
                    fig.update_layout(
                        title="Account Equity & Drawdown Over Time",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#94a3b8',
                        margin=dict(l=0, r=0, t=40, b=0),
                        showlegend=False,
                        hovermode="x unified"
                    )
                    fig.update_xaxes(title_text="Trade Number", showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                    fig.update_yaxes(title_text="Account Balance ($)", showgrid=True, gridcolor='rgba(255,255,255,0.05)', secondary_y=False, tickformat=".2f")
                    fig.update_yaxes(title_text="Drawdown (%)", showgrid=False, secondary_y=True, range=y2_range, tickformat=".2f")
                    if key:
                        st.plotly_chart(fig, use_container_width=True, key=key)
                    else:
                        st.plotly_chart(fig, use_container_width=True)
                        
                    # Advanced Analytics: Monte Carlo
                    if 'Profit' in deals_df.columns:
                        with st.expander("🎲 Advanced Analytics: Monte Carlo Simulation"):
                            st.write("This simulation randomly shuffles your historical trades 500 times to map the probability distribution of potential future equity curves, revealing the absolute worst-case drawdowns.")
                            
                            deals_df['Profit'] = deals_df['Profit'].astype(str).str.replace(' ', '')
                            deals_df['Profit'] = pd.to_numeric(deals_df['Profit'], errors='coerce')
                            profits = deals_df.dropna(subset=['Profit'])['Profit'].values
                            
                            if len(profits) > 0:
                                import numpy as np
                                n_simulations = 500
                                start_balance = deals_df['Balance'].iloc[0] - profits[0] if len(deals_df) > 0 else 10000
                                
                                mc_fig = go.Figure()
                                worst_dd = 0
                                
                                # We won't plot all 500 to save memory, maybe 50 random paths, but calculate stats on 500
                                sim_paths = []
                                for i in range(n_simulations):
                                    shuffled = np.random.choice(profits, size=len(profits), replace=True)
                                    path = np.concatenate(([start_balance], start_balance + np.cumsum(shuffled)))
                                    sim_paths.append(path)
                                    
                                    # Calculate DD
                                    peaks = np.maximum.accumulate(path)
                                    drawdowns = (peaks - path) / peaks
                                    max_d = np.max(drawdowns)
                                    if max_d > worst_dd:
                                        worst_dd = max_d
                                        
                                    if i < 50:
                                        mc_fig.add_trace(go.Scatter(y=path, mode='lines', line=dict(color='rgba(139, 92, 246, 0.05)', width=1), showlegend=False, hoverinfo='skip'))
                                
                                # Add original path
                                original_path = np.concatenate(([start_balance], start_balance + np.cumsum(profits)))
                                mc_fig.add_trace(go.Scatter(y=original_path, mode='lines', name="Original", line=dict(color='#3b82f6', width=3)))
                                
                                # Add Mean path
                                mean_path = np.mean(sim_paths, axis=0)
                                mc_fig.add_trace(go.Scatter(y=mean_path, mode='lines', name="Mean Path", line=dict(color='#ef4444', width=2, dash='dash')))
                                
                                mc_fig.update_layout(
                                    title=f"Monte Carlo ({n_simulations} Sims) | Est. Worst Drawdown: {worst_dd*100:.2f}%",
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    font_color='#94a3b8',
                                    margin=dict(l=0, r=0, t=40, b=0),
                                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                                )
                                mc_key = f"mc_{key}" if key else "mc_default"
                                st.plotly_chart(mc_fig, use_container_width=True, key=mc_key)
                            else:
                                st.info("No valid profit data found for Monte Carlo.")
                else:
                    st.info("Could not extract Equity Curve data from Deals.")
        else:
            st.info("No Deals found in the report.")

def render_ai_analysis(metrics, api_key):
    with st.expander("🧠 AI Strategy Analyst"):
        if not api_key:
            st.warning("Please enter your Gemini API Key in the sidebar to unlock AI Analysis.")
            return
            
        st.write("Click below to generate a comprehensive AI analysis of this strategy's metrics.")
        if st.button("Generate AI Analysis", key=f"ai_btn_{metrics.get('Total Trades', '0')}"):
            model_name = st.session_state.get('gemini_model_name', 'models/gemini-1.5-pro-latest')
            with st.spinner(f"Analyzing metrics with {model_name}..."):
                try:
                    import google.generativeai as genai
                    model = genai.GenerativeModel(model_name)
                    
                    prompt = f"""
                    You are a senior quantitative trading analyst. Review the following MT5 backtest metrics and provide a concise, brutally honest assessment.
                    
                    Metrics:
                    - Total Net Profit: {metrics.get('Total Net Profit')}
                    - Max Drawdown: {metrics.get('Max Drawdown')}
                    - Win Rate: {metrics.get('Win Rate')}
                    - Profit Factor: {metrics.get('Profit Factor')}
                    - Total Trades: {metrics.get('Total Trades')}
                    - Recovery Factor: {metrics.get('Recovery Factor')}
                    - Calmar Ratio (Est): {metrics.get('Calmar Ratio (Est)')}
                    
                    Please structure your response into:
                    1. **Strengths**: What is working well?
                    2. **Weaknesses/Risks**: What are the hidden dangers (e.g. overfitting, martingale, low trades)?
                    3. **Recommendations**: Concrete steps to improve.
                    """
                    
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI Analysis failed: {e}")

def parse_ea_inputs(raw_inputs):
    ea_inputs = {}
    if raw_inputs.strip():
        for line in raw_inputs.strip().split('\n'):
            if '=' in line:
                k, v = line.split('=', 1)
                ea_inputs[k.strip()] = v.strip()
    return ea_inputs

def main():
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
    
    # Calculate dollar risk based on session state to update label dynamically
    current_risk = st.session_state.get('risk_percent_slider', 2.0)
    risk_money = (current_risk / 100.0) * initial_balance
    
    risk_percent = st.sidebar.slider(
        f"Risk per Trade [%] (${risk_money:.2f})", 
        min_value=0.1, max_value=20.0, value=2.0, step=0.1,
        key='risk_percent_slider'
    )
    
    st.sidebar.markdown("---")
    st.sidebar.header("⏱️ 3. Trading Filter")
    
    # Session selector
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
    
    # Process trading hours string
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
    
    # Inject the UI config into the EA inputs
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
            # Try to default to saved model, or fallback to flash or pro
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
            
            # Auto-save logic
            if gemini_api_key != saved_api_key or selected_model != saved_model:
                settings["gemini_api_key"] = gemini_api_key
                settings["gemini_model_name"] = selected_model
                save_settings(settings)
                
        except Exception as e:
            st.sidebar.error(f"Error fetching models: {e}")
            st.session_state['gemini_model_name'] = 'gemini-1.5-pro'
    else:
        # If they clear the key, auto-save the cleared state
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
                        
                        # Parse immediately to save to DB
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
                            # db operations are thread-safe as we connect/disconnect each time
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
                
                # Note: MT5 terminal natively overrides/locks its own instance if run from the same installation folder concurrently.
                # Running them with max_workers=1 ensures true sequential stability without file locking crashes.
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
            
            # Export to CSV
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
                
                # Create the .set file content
                set_content = ""
                for k, v in ea_inputs.items():
                    set_content += f"{k}={v}\n"
                    
                # Create ZIP in memory
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    # Add the EX5 file
                    zf.write(ex5_path, arcname=f"MQL5/Experts/{ea_name}")
                    # Add the SET file
                    zf.writestr(f"MQL5/Presets/{ea_name.replace('.ex5', '')}_Optimized.set", set_content)
                    
                    # Add a README
                    readme_content = f"Deployment Instructions for {ea_name}:\n\n1. Extract this ZIP into your MetaTrader 5 Data Folder.\n2. Open MT5, refresh your Navigator panel.\n3. Drag {ea_name} onto a chart.\n4. Click 'Load' and select the Preset file located in MQL5/Presets/.\n5. Enable AutoTrading!"
                    zf.writestr("README.txt", readme_content)
                
                # Provide download button
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
