import plotly.graph_objects as go
import pandas as pd

def plot_equity_curve(equity_series: pd.Series) -> go.Figure:
    """
    Plots the equity curve using Plotly.
    """
    fig = go.Figure()
    
    # Check if we have data
    if equity_series is None or equity_series.empty:
        fig.add_annotation(text="No equity data available", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(xaxis_visible=False, yaxis_visible=False)
        return fig
        
    # Convert index to string if it's datetime to avoid gaps in plotly sometimes, 
    # but plotly usually handles continuous time series well.
    fig.add_trace(go.Scatter(
        x=equity_series.index,
        y=equity_series.values,
        mode='lines',
        name='Equity',
        line=dict(color='#00b4d8', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 180, 216, 0.1)'
    ))
    
    fig.update_layout(
        title="Portfolio Equity Curve",
        xaxis_title="Time",
        yaxis_title="Portfolio Value ($)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)')
    )
    
    return fig
