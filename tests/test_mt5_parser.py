import os

import pandas as pd
import pytest

from services.mt5_parser import (
    extract_all_metrics,
    extract_metric,
    parse_ea_inputs,
    parse_mt5_html_cached,
    parse_optimization_xml,
)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_REPORT = os.path.join(FIXTURES_DIR, "sample_report.htm")
SAMPLE_OPTIMIZATION = os.path.join(FIXTURES_DIR, "sample_optimization.xml")


@pytest.fixture(scope="module")
def report_df():
    tables = parse_mt5_html_cached(SAMPLE_REPORT)
    return tables[0]


def test_parse_mt5_html_cached_returns_tables(report_df):
    assert isinstance(report_df, pd.DataFrame)
    assert not report_df.empty


def test_extract_metric_finds_adjacent_value(report_df):
    assert extract_metric(report_df, "Total Net Profit:") == "1 234.56"
    assert extract_metric(report_df, "Profit Factor:") == "2.61"
    assert extract_metric(report_df, "Equity Drawdown Maximal:") == "500.00 (5.00%)"


def test_extract_metric_missing_returns_na(report_df):
    assert extract_metric(report_df, "Nonexistent Metric:") == "N/A"


def test_extract_all_metrics(report_df):
    metrics = extract_all_metrics(report_df)
    assert metrics["Total Net Profit"] == "1 234.56"
    assert metrics["Gross Profit"] == "2 000.00"
    assert metrics["Gross Loss"] == "-765.44"
    assert metrics["Profit Factor"] == "2.61"
    assert metrics["Total Trades"] == "42"
    assert metrics["Expected Payoff"] == "29.39"
    assert metrics["Sharpe Ratio"] == "1.85"
    assert metrics["Max Drawdown"] == "500.00 (5.00%)"
    assert metrics["Win Rate"] == "30 (71.43%)"
    assert metrics["Recovery Factor"] == "2.47"
    assert metrics["History Quality"] == "100%"
    assert metrics["Max Cons. Wins"] == "350.00 (6)"


def test_extract_all_metrics_calmar_ratio(report_df):
    metrics = extract_all_metrics(report_df)
    # 1234.56 / 500.00 = 2.47
    assert metrics["Calmar Ratio (Est)"] == "2.47"


def test_extract_all_metrics_calmar_na_when_missing():
    df = pd.DataFrame([["Some Label:", "1.00"]])
    metrics = extract_all_metrics(df)
    assert metrics["Total Net Profit"] == "N/A"
    assert metrics["Calmar Ratio (Est)"] == "N/A"


def test_parse_optimization_xml(report_df):
    df = parse_optimization_xml(SAMPLE_OPTIMIZATION)
    assert list(df.columns) == ["Pass", "Profit", "Drawdown"]
    assert len(df) == 2
    assert df["Profit"].tolist() == [1500.50, -300.00]
    assert df["Drawdown"].tolist() == [120.25, 450.75]


def test_parse_optimization_xml_no_rows_returns_empty(tmp_path):
    empty_file = tmp_path / "empty.xml"
    empty_file.write_text("<Workbook></Workbook>", encoding="utf-16")
    df = parse_optimization_xml(str(empty_file))
    assert df.empty


def test_parse_ea_inputs():
    raw = "InpFastMA=10\nInpSlowMA = 50\nInpRiskPercentage=2.0\nnot a pair\n"
    assert parse_ea_inputs(raw) == {
        "InpFastMA": "10",
        "InpSlowMA": "50",
        "InpRiskPercentage": "2.0",
    }


def test_parse_ea_inputs_empty():
    assert parse_ea_inputs("   ") == {}
