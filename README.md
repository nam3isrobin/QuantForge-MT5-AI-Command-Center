# ⚡ QuantForge: MT5 AI Command Center

The **QuantForge: MT5 AI Command Center** is a professional-grade graphical interface designed for quantitative developers and algorithmic traders. Instead of relying on the clunky, native MetaTrader 5 interface, this command center wraps the MT5 engine into a highly aesthetic, responsive, and data-rich web application. It automates the generation of MT5 `.ini` files, interacts with the native `terminal64.exe` CLI, extracts strategy metrics, and features an integrated **AI Strategy Analyst** powered by Google Gemini.

## 🌟 Key Features

* **Glassmorphic Streamlit UI**: A beautiful, dark-mode native web interface for managing your MT5 backtests.
* **Batch Testing**: Run multiple backtests across different symbols natively using Python's `ThreadPoolExecutor`.
* **AI Strategy Analyst**: Paste your Google Gemini API key to get instant, brutally honest quantitative analysis of your EA's performance (Drawdown, Calmar Ratio, Recovery Factor).
* **Monte Carlo Simulations**: Visualizes 500 potential probability cones for your equity curve to estimate worst-case drawdowns.
* **History Ledger (SQLite)**: Automatically archives every single backtest run, allowing you to load up past equity curves instantly or export them to CSV.

## 🚀 Setup & Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/nam3isrobin/QuantForge-MT5-AI-Command-Center.git
   cd QuantForge-MT5-AI-Command-Center
   ```

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Settings**:
   Copy `settings.example.json` to `settings.json` (this file is gitignored so your API key never gets committed):
   ```bash
   copy settings.example.json settings.json
   ```
   The app reads the Gemini API key and model name from `settings.json`; if it is missing, it falls back to the empty `settings.example.json` template.

5. **Configure MT5 Path**:
   Open `config.py` and modify the `DEFAULT_MT5_TERMINAL_PATH` and `DEFAULT_MT5_DATA_PATH` to point to your broker's MetaTrader 5 installation on your PC.
   ```python
   # Example
   DEFAULT_MT5_TERMINAL_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
   ```

## 🎮 Running the App

```bash
streamlit run app.py
```

1. **Upload an Expert Advisor**: Use the sidebar to upload any compiled `.ex5` file.
2. **Set Parameters**: Adjust your starting deposit, dates, and input strings (e.g. `InpFastMA=10`).
3. **Run Backtests**: Hit the Run button to dynamically dispatch the headless MT5 engine!

### ⚠️ EA Compatibility Requirements
QuantForge dynamically overrides specific variables in your Expert Advisor to control risk and trading hours via the UI. For these specific UI toggles to take effect, your `.mq5` code **must** expose the following input parameters:
```cpp
input double InpRiskPercentage = 2.0; // Controls dynamic lot sizing
input string InpTradingHours   = "0-23"; // Controls session filters (e.g. "8-12, 14-17")
```
*Note: If your EA does not use these exact input names, it will still backtest perfectly, but the Risk slider and Session checkboxes in the sidebar will simply have no effect on your strategy.*

## 🧠 Using the AI Analyst
To use the Gemini AI features:
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Paste it into the **AI Analyst Configuration** block in the sidebar.
3. The UI will automatically detect all AI models available to your key. Select one, expand the AI section under your equity curve, and click **Generate AI Analysis**.

## 🧪 Running the Tests
Unit tests cover the MT5 report parser (`services/mt5_parser.py`) using sample HTML/XML report fixtures in `tests/fixtures/`.

```bash
pip install -r requirements-dev.txt
python -m pytest tests/
```

## 🛠 Tech Stack
* **Frontend**: Streamlit, Plotly, Custom CSS
* **Backend**: Python 3, SQLite
* **AI Integration**: `google-generativeai` 
* **Trading Engine**: MetaTrader 5 Native CLI (`terminal64.exe`)

## 🤝 Contributing
Pull requests are welcome! If you want to add Walk-Forward Optimization, integration with local LLMs, or support for passing custom historical tick data, feel free to fork the repository!

---
*Disclaimer: QuantForge is a tool for quantitative research and educational purposes. Algorithmic trading in financial markets carries a high degree of risk and may not be suitable for all investors. Past performance is not indicative of future results.*
#
