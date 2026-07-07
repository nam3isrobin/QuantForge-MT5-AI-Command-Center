import os
import shutil
import subprocess
import time
from datetime import datetime
import config

def run_mt5_cli_backtest(
    ex5_path: str,
    symbol: str,
    timeframe: str,
    start_date: datetime,
    end_date: datetime,
    initial_deposit: float = 10000.0,
    leverage: int = 100,
    ea_inputs: dict = None,
    optimization: int = 0
) -> str:
    """
    Copies the EX5 file to MT5, generates a config.ini, runs the backtest in headless mode,
    and returns the path to the generated XML report.
    """
    terminal_path = config.DEFAULT_MT5_TERMINAL_PATH
    data_path = config.DEFAULT_MT5_DATA_PATH
    
    if not os.path.exists(terminal_path):
        raise FileNotFoundError(f"MT5 terminal not found at: {terminal_path}")
        
    # 1. Copy the EA to the MT5 Experts folder
    experts_dir = os.path.join(data_path, "MQL5", "Experts", "TesterApp")
    os.makedirs(experts_dir, exist_ok=True)
    
    ea_name = os.path.basename(ex5_path)
    dest_ex5 = os.path.join(experts_dir, ea_name)
    shutil.copy2(ex5_path, dest_ex5)
    
    # MT5 config expects the EA name without extension relative to MQL5 directory
    ea_name_no_ext = ea_name.replace('.ex5', '')
    ea_relative_path = f"TesterApp\\{ea_name_no_ext}"
    
    import uuid
    unique_suffix = uuid.uuid4().hex[:6]
    report_name = f"Report_{ea_name_no_ext}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{unique_suffix}"
    # MT5 automatically appends .xml to optimization reports and .htm to single backtest reports
    report_filename = f"{report_name}.xml" if optimization > 0 else f"{report_name}.htm"
    report_path_out = os.path.join(config.REPORTS_DIR, report_filename)
    
    # Format dates to YYYY.MM.DD
    str_start = start_date.strftime("%Y.%m.%d")
    str_end = end_date.strftime("%Y.%m.%d")
    
    ini_content = f"""[Tester]
Expert={ea_relative_path}
Symbol={symbol}
Period={timeframe}
Model=0
ExecutionMode=0
Optimization={optimization}
OptimizationCriterion=0
FromDate={str_start}
ToDate={str_end}
ForwardMode=0
Report={report_name}
ReplaceReport=1
ShutdownTerminal=1
Deposit={initial_deposit}
Currency=USD
Leverage=1:{leverage}
Visual=0
"""
    if ea_inputs:
        # For optimization to work in MT5 CLI, we MUST create a .set file in MQL5/Profiles/Tester
        # and it MUST be encoded in utf-16le. [TesterInputs] in the .ini does NOT support optimization.
        tester_profiles_dir = os.path.join(data_path, "MQL5", "Profiles", "Tester", "TesterApp")
        os.makedirs(tester_profiles_dir, exist_ok=True)
        
        set_file_path = os.path.join(tester_profiles_dir, f"{ea_name_no_ext}.set")
        set_content = ""
        for key, value in ea_inputs.items():
            if '||' in str(value):
                parts = str(value).split('||')
                if len(parts) == 4:
                    v, start, step, stop = parts
                    set_content += f"{key}={v}||{start}||{step}||{stop}||Y\n"
                else:
                    set_content += f"{key}={value}\n"
            else:
                set_content += f"{key}={value}||0.0||0.0||0.0||N\n"
                
        with open(set_file_path, "w", encoding="ansi") as f:
            f.write(set_content)
        
        # Tell the INI to use this .set file
        ini_content += f"ExpertParameters=TesterApp\\{ea_name_no_ext}.set\n"
    
    import uuid
    unique_id = uuid.uuid4().hex[:8]
    ini_path = os.path.join(config.BASE_DIR, f"backtest_{unique_id}.ini")
    with open(ini_path, "w", encoding="ansi") as f:
        f.write(ini_content)
        
    # 3. Execute MT5 Terminal in headless mode
    # Note: Removed taskkill to allow multiple instances to run concurrently
    
    # Use powershell Start-Process -Wait to block until MT5 finishes
    ps_command = f"Start-Process -FilePath '{terminal_path}' -ArgumentList '/config:{ini_path}' -Wait"
    
    try:
        subprocess.run(["powershell", "-Command", ps_command], check=True)
    except subprocess.CalledProcessError as e:
        if os.path.exists(ini_path):
            os.remove(ini_path)
        raise RuntimeError(f"MT5 execution failed: {e}")
        
    # 4. Poll for the report generation
    possible_output_paths = [
        os.path.join(data_path, report_filename),
        os.path.join(data_path, "Tester", report_filename),
        os.path.join(data_path, "MQL5", "Files", report_filename)
    ]
    
    timeout = 90
    elapsed = 0
    found_path = None
    
    while elapsed < timeout:
        for p in possible_output_paths:
            if os.path.exists(p):
                found_path = p
                break
        if found_path:
            break
        time.sleep(1)
        elapsed += 1
        
    # Clean up the dynamic ini file
    if os.path.exists(ini_path):
        os.remove(ini_path)
        
    if not found_path:
        raise FileNotFoundError(f"MT5 Report not generated within {timeout} seconds. Tips: 1) Verify the symbol exactly matches your broker (e.g. BTCUSD vs BTCUSD.m). 2) MT5 might be downloading historical data, which takes time on the first run.")
        
    # 5. Move the report to the reports directory
    shutil.move(found_path, report_path_out)
    
    # Move any associated PNG files (graphs generated by MT5)
    import glob
    base_dir = os.path.dirname(found_path)
    base_name = os.path.splitext(os.path.basename(found_path))[0] # e.g. "Report"
    
    png_pattern = os.path.join(base_dir, f"{base_name}*.png")
    for png_file in glob.glob(png_pattern):
        dest_png = os.path.join(config.REPORTS_DIR, os.path.basename(png_file))
        if os.path.exists(dest_png):
            os.remove(dest_png)
        shutil.move(png_file, dest_png)
        
    return report_path_out
