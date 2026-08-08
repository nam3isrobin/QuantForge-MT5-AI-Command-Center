import streamlit as st
import pandas as pd

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            background-color: #0d0405 !important;
            color: #FCF2F4 !important;
        }
        
        .stApp {
            background-color: #0d0405 !important;
            color: #FCF2F4 !important;
        }
        
        h1, h2, h3, h4, h5, h6, .st-emotion-cache-10trblm {
            font-family: 'Outfit', sans-serif !important;
            -webkit-text-fill-color: initial !important;
            color: #FCF2F4 !important;
        }
        
        .glass-header {
            position: sticky;
            top: 0;
            z-index: 60;
            background: rgba(13, 4, 5, 0.6);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 59, 92, 0.2);
            padding: 1rem 2rem;
            margin: 1rem auto 2rem auto;
            border-radius: 9999px; /* Pill shape */
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
            text-align: center;
            max-width: 90%;
        }
        .glass-header h1 {
            margin: 0 !important;
            padding: 0 !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
            color: #ff3b5c !important;
        }
        
        /* Glassmorphic Container for Metrics */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 59, 92, 0.15);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        [data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
            font-family: monospace, monospace !important;
            font-variant-numeric: tabular-nums;
            font-weight: 700 !important;
            color: #FCF2F4 !important;
        }
        [data-testid="stMetricLabel"] {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1rem !important;
            color: #F59E0B !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Hover effects */
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border: 1px solid rgba(255, 59, 92, 0.4);
        }
        
        /* Glass Buttons */
        div.stButton > button, a[data-testid="stLinkButton"] {
            background-color: #ff3b5c !important;
            color: #0d0405 !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 2rem !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        div.stButton > button:hover, a[data-testid="stLinkButton"]:hover {
            background-color: #ff5271 !important;
            transform: scale(1.02) !important;
        }
        
        [data-testid="stSidebar"] {
            background: rgba(13, 4, 5, 0.9) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 59, 92, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

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
                            fillcolor='rgba(16, 185, 129, 0.2)', # Emerald
                            line=dict(color='#10B981', width=2),
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
                            fillcolor='rgba(255, 59, 92, 0.1)', # Crimson
                            line=dict(color='#ff3b5c', width=1),
                            hovertemplate="Drawdown: %{y:.2f}%<extra></extra>"
                        ),
                        secondary_y=True
                    )
                    
                    max_dd = deals_df['Drawdown'].max()
                    y2_range = [max_dd * 1.5 if max_dd > 0 else 10, 0]
                    
                    fig.update_layout(
                        title="Account Equity & Drawdown Over Time",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#FCF2F4',
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
                                
                                sim_paths = []
                                for i in range(n_simulations):
                                    shuffled = np.random.choice(profits, size=len(profits), replace=True)
                                    path = np.concatenate(([start_balance], start_balance + np.cumsum(shuffled)))
                                    sim_paths.append(path)
                                    
                                    peaks = np.maximum.accumulate(path)
                                    drawdowns = (peaks - path) / peaks
                                    max_d = np.max(drawdowns)
                                    if max_d > worst_dd:
                                        worst_dd = max_d
                                        
                                    if i < 50:
                                        mc_fig.add_trace(go.Scatter(y=path, mode='lines', line=dict(color='rgba(16, 185, 129, 0.05)', width=1), showlegend=False, hoverinfo='skip'))
                                
                                original_path = np.concatenate(([start_balance], start_balance + np.cumsum(profits)))
                                mc_fig.add_trace(go.Scatter(y=original_path, mode='lines', name="Original", line=dict(color='#10B981', width=3)))
                                
                                mean_path = np.mean(sim_paths, axis=0)
                                mc_fig.add_trace(go.Scatter(y=mean_path, mode='lines', name="Mean Path", line=dict(color='#ff3b5c', width=2, dash='dash')))
                                
                                mc_fig.update_layout(
                                    title=f"Monte Carlo ({n_simulations} Sims) | Est. Worst Drawdown: {worst_dd*100:.2f}%",
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    font_color='#FCF2F4',
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
