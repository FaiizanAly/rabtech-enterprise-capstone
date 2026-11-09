"""Unit tests verifying data fetching, BI processing, PDF creation, and CLI pipeline."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from capstone_engine.cli import run_pipeline, main
from capstone_engine.fetcher import FinancialDataFetcher, DEFAULT_ENTERPRISE_DATA
from capstone_engine.pdf_generator import FinancialReportGenerator, fmt_currency
from capstone_engine.processor import FinancialProcessor


def test_currency_formatter():
    assert fmt_currency(1250000.5) == "$1,250,000.50"
    assert fmt_currency(0.0) == "$0.00"


def test_fetcher_default_data():
    fetcher = FinancialDataFetcher()
    records = fetcher.fetch_records()
    assert len(records) == len(DEFAULT_ENTERPRISE_DATA)
    assert records[0]["department"] == "Cloud Solutions"


@patch("capstone_engine.fetcher.requests.get")
def test_fetcher_remote_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {"quarter": "Q1 2026", "department": "Security", "revenue": 500000.0, "expenses": 300000.0}
    ]
    mock_get.return_value = mock_resp

    fetcher = FinancialDataFetcher(endpoint_url="http://example.com/api/data")
    records = fetcher.fetch_records()
    assert len(records) == 1
    assert records[0]["department"] == "Security"


@patch("capstone_engine.fetcher.requests.get")
def test_fetcher_remote_failure_fallback(mock_get):
    mock_get.side_effect = Exception("Connection refused")

    fetcher = FinancialDataFetcher(endpoint_url="http://invalid.domain/api")
    records = fetcher.fetch_records()
    assert len(records) == len(DEFAULT_ENTERPRISE_DATA)


def test_processor_metrics_calculation():
    sample = [
        {"quarter": "Q1", "department": "DevOps", "revenue": 1000.0, "expenses": 600.0, "budget": 700.0},
        {"quarter": "Q1", "department": "AI", "revenue": 2000.0, "expenses": 1000.0, "budget": 1100.0},
    ]
    processor = FinancialProcessor(sample)
    kpis = processor.compute_summary_kpis()

    assert kpis["total_revenue"] == 3000.0
    assert kpis["total_expenses"] == 1600.0
    assert kpis["net_profit"] == 1400.0
    assert kpis["profit_margin_pct"] == 46.67
    assert kpis["budget_variance"] == 200.0

    depts = processor.aggregate_by_department()
    assert len(depts) == 2
    assert depts[0]["department"] == "AI"
    assert depts[0]["net_profit"] == 1000.0

    quarters = processor.aggregate_by_quarter()
    assert len(quarters) == 1
    assert quarters[0]["quarter"] == "Q1"


def test_processor_empty_records_error():
    with pytest.raises(ValueError):
        FinancialProcessor([])


def test_pdf_report_generation(tmp_path: Path):
    sample = [
        {"quarter": "Q1 2026", "department": "Cloud", "revenue": 100000.0, "expenses": 50000.0, "budget": 60000.0}
    ]
    processor = FinancialProcessor(sample)
    kpis = processor.compute_summary_kpis()
    dept_data = processor.aggregate_by_department()
    q_data = processor.aggregate_by_quarter()

    pdf_out = tmp_path / "test_report.pdf"
    generator = FinancialReportGenerator(output_path=pdf_out)
    result_path = generator.build_pdf(kpis, dept_data, q_data)

    assert result_path.exists()
    assert result_path.stat().st_size > 1000  # PDF generated with content


def test_pipeline_and_cli(tmp_path: Path):
    target_pdf = tmp_path / "cli_report.pdf"
    res = run_pipeline(output_path=target_pdf)
    assert res.exists()

    with patch("sys.argv", ["capstone-report", "--output", str(target_pdf)]):
        main()
    assert target_pdf.exists()
