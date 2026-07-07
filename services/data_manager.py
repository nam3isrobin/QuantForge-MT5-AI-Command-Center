import os
import pandas as pd
from datetime import datetime
from typing import Optional

# To handle imports depending on whether it's run from app.py or directly
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CACHE_DIR, TIMEFRAME_MAPPING
from services.mt5_connector import fetch_rates
from services.csv_loader import load_csv

def get_data(symbol: str, timeframe: str, start: datetime, end: datetime, use_mt5: bool = True, csv_file=None) -> Optional[pd.DataFrame]:
    """
    Orchestrates data fetching. Either grabs from MT5 and caches it, or loads from CSV.
    """
    if not use_mt5:
        if csv_file is not None:
            return load_csv(csv_file)
        return None
        
    if use_mt5:
        if timeframe not in TIMEFRAME_MAPPING:
            print(f"Invalid timeframe: {timeframe}")
            return None
            
        mt5_tf = TIMEFRAME_MAPPING[timeframe]
        df = fetch_rates(symbol, mt5_tf, start, end)
        
        if df is not None and not df.empty:
            # Cache the data
            cache_file = os.path.join(CACHE_DIR, f"{symbol}_{timeframe}.parquet")
            try:
                df.to_parquet(cache_file, engine='fastparquet')
            except Exception as e:
                print(f"Warning: Failed to cache data to {cache_file}: {e}")
                
        return df
            
    return None
