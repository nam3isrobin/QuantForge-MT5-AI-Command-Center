import pandas as pd
import re

def parse_mt5_html_cached(report_path):
    return pd.read_html(report_path, encoding='utf-16')

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
    except (ValueError, TypeError, ZeroDivisionError):
        metrics['Calmar Ratio (Est)'] = "N/A"
        
    return metrics

def parse_ea_inputs(raw_inputs):
    ea_inputs = {}
    if raw_inputs.strip():
        for line in raw_inputs.strip().split('\n'):
            if '=' in line:
                k, v = line.split('=', 1)
                ea_inputs[k.strip()] = v.strip()
    return ea_inputs
