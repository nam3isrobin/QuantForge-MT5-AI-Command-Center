import sqlite3
import os
import json
from datetime import datetime
import config

DB_PATH = os.path.join(config.BASE_DIR, "database", "backtests.db")

def init_db():
    """Initializes the SQLite database and creates the necessary tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backtest_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ea_name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            inputs_json TEXT,
            net_profit REAL,
            gross_profit REAL,
            gross_loss REAL,
            profit_factor REAL,
            total_trades INTEGER,
            expected_payoff REAL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            win_rate TEXT,
            recovery_factor REAL,
            history_quality TEXT,
            max_cons_wins TEXT,
            report_path TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_backtest_result(ea_name, symbol, timeframe, start_date, end_date, inputs, metrics, report_path):
    """Saves a single backtest run to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Safe float parsing
    def safe_float(val):
        try:
            return float(str(val).replace(' ', ''))
        except (ValueError, TypeError):
            return 0.0
            
    def safe_int(val):
        try:
            return int(str(val).replace(' ', ''))
        except (ValueError, TypeError):
            return 0
    
    inputs_json = json.dumps(inputs) if inputs else "{}"
    
    cursor.execute('''
        INSERT INTO backtest_runs (
            timestamp, ea_name, symbol, timeframe, start_date, end_date, 
            inputs_json, net_profit, gross_profit, gross_loss, profit_factor,
            total_trades, expected_payoff, sharpe_ratio, max_drawdown, 
            win_rate, recovery_factor, history_quality, max_cons_wins, report_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ea_name, symbol, timeframe, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"),
        inputs_json,
        safe_float(metrics.get("Total Net Profit", 0)),
        safe_float(metrics.get("Gross Profit", 0)),
        safe_float(metrics.get("Gross Loss", 0)),
        safe_float(metrics.get("Profit Factor", 0)),
        safe_int(metrics.get("Total Trades", 0)),
        safe_float(metrics.get("Expected Payoff", 0)),
        safe_float(metrics.get("Sharpe Ratio", 0)),
        safe_float(metrics.get("Max Drawdown", 0)),
        str(metrics.get("Win Rate", "0%")),
        safe_float(metrics.get("Recovery Factor", 0)),
        str(metrics.get("History Quality", "0%")),
        str(metrics.get("Max Cons. Wins", "0 (0)")),
        report_path
    ))
    
    conn.commit()
    conn.close()

def get_all_backtests():
    """Retrieves all backtests from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM backtest_runs ORDER BY id DESC")
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in rows]

def delete_backtest(run_id):
    """Deletes a specific backtest run from the database by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM backtest_runs WHERE id = ?", (run_id,))
    conn.commit()
    conn.close()

def clear_all_backtests():
    """Deletes all backtest runs from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM backtest_runs")
    conn.commit()
    conn.close()
