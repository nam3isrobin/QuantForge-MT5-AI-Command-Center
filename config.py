import os
import MetaTrader5 as mt5

# Base project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "data_cache")
STRATEGIES_DIR = os.path.join(BASE_DIR, "strategies")
REPORTS_DIR = os.path.join(BASE_DIR, "static", "reports")

# Ensure directories exist
for directory in [CACHE_DIR, STRATEGIES_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Default configuration
DEFAULT_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]

# MT5 Timeframe mapping
TIMEFRAME_MAPPING = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}

# App Configurations
DEFAULT_CAPITAL = 10000.0
DEFAULT_COMMISSION = 0.001
DEFAULT_TIMEFRAME = 'M1'

# Option B: MT5 CLI Paths
DEFAULT_MT5_TERMINAL_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"

# Dynamically find the correct MT5 Data folder in AppData to avoid initialization failures
appdata_path = os.path.join(os.environ.get('APPDATA', ''), 'MetaQuotes', 'Terminal')
found_data_path = r"C:\Program Files\MetaTrader 5"

if os.path.exists(appdata_path):
    # Find the 32-character hash folder (like D0E8209F77C8CF37AD8BF550E51FF075)
    for folder_name in os.listdir(appdata_path):
        folder_path = os.path.join(appdata_path, folder_name)
        if len(folder_name) == 32 and os.path.isdir(folder_path):
            found_data_path = folder_path
            break

DEFAULT_MT5_DATA_PATH = found_data_path
