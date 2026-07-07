import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

def initialize_mt5():
    """
    Initializes the MetaTrader 5 connection.
    Returns True if successful, False otherwise.
    """
    if mt5.initialize():
        info = mt5.terminal_info()
        if info is not None and info.connected:
            return True
        # Initialized but not connected to a broker
        mt5.shutdown()
    return False

def fetch_rates(symbol: str, timeframe: int, start: datetime, end: datetime) -> pd.DataFrame:
    """
    Fetches OHLCV rates from MT5.
    Returns an empty DataFrame if no data is found or an error occurs.
    """
    if not initialize_mt5():
        print("Failed to initialize MT5")
        return pd.DataFrame()
        
    rates = mt5.copy_rates_range(symbol, timeframe, start, end)
    
    if rates is None or len(rates) == 0:
        print(f"No rates found for {symbol}")
        return pd.DataFrame()
        
    df = pd.DataFrame(rates)
    # MT5 returns time in seconds
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    return df

def shutdown_mt5():
    """
    Gracefully shuts down MT5 connection.
    """
    mt5.shutdown()
