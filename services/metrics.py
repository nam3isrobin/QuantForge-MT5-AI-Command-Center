from typing import Dict, Any

def calculate_summary_stats(results: Dict[str, Any], initial_cash: float) -> Dict[str, Any]:
    """
    Extracts and calculates key metrics from the backtest results.
    """
    final_value = results.get('final_value', initial_cash)
    total_return = ((final_value - initial_cash) / initial_cash) * 100
    
    trades_info = results.get('trades_info', {})
    total_trades = trades_info.get('total', {}).get('total', 0)
    
    won = trades_info.get('won', {}).get('total', 0)
    lost = trades_info.get('lost', {}).get('total', 0)
    win_rate = (won / total_trades * 100) if total_trades > 0 else 0.0
    
    # Profit factor: gross profit / gross loss
    gross_profit = trades_info.get('won', {}).get('pnl', {}).get('total', 0.0)
    gross_loss = abs(trades_info.get('lost', {}).get('pnl', {}).get('total', 0.0))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (float('inf') if gross_profit > 0 else 0.0)
    
    # Drawdown
    drawdown_info = results.get('drawdown', {})
    max_drawdown = drawdown_info.get('max', {}).get('drawdown', 0.0)
    
    # Sharpe
    sharpe_info = results.get('sharpe', {})
    sharpe_ratio = sharpe_info.get('sharperatio', 0.0)
    if sharpe_ratio is None:
        sharpe_ratio = 0.0
        
    return {
        "Total Return (%)": round(total_return, 2),
        "Max Drawdown (%)": round(max_drawdown, 2),
        "Sharpe Ratio": round(sharpe_ratio, 2),
        "Total Trades": total_trades,
        "Win Rate (%)": round(win_rate, 2),
        "Profit Factor": round(profit_factor, 2)
    }
