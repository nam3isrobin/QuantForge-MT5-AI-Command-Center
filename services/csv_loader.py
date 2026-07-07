import pandas as pd
from typing import Optional

def load_csv(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Reads an uploaded CSV file into a pandas DataFrame.
    Expects standard OHLCV columns (time, open, high, low, close, tick_volume/volume).
    """
    try:
        df = pd.read_csv(uploaded_file)
        
        # Make column names lowercase for standardization
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # Standardize date/time column
        if 'time' not in df.columns and 'date' in df.columns:
            df.rename(columns={'date': 'time'}, inplace=True)
            
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
            
        # Standardize volume column
        if 'tick_volume' not in df.columns and 'volume' in df.columns:
             df.rename(columns={'volume': 'tick_volume'}, inplace=True)
             
        # Validate required columns
        required_cols = ['time', 'open', 'high', 'low', 'close']
        if not all(col in df.columns for col in required_cols):
            print(f"Missing required columns. Found: {df.columns}")
            return None
            
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None
