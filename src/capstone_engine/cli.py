"""Command Line Interface (CLI) driving the automated report generation pipeline."""

import argparse
import logging
import sys
from pathlib import Path

from capstone_engine.fetcher import FinancialDataFetcher
from capstone_engine.pdf_generator import FinancialReportGenerator, fmt_currency
from capstone_engine.processor import FinancialProcessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("capstone_engine")


def run_pipeline(output_path: Path, endpoint: str = None) -> Path:
    """Run data ingestion, analytics computation, and PDF report compilation."""
    logger.info("Initializing financial data fetcher...")
    fetcher = FinancialDataFetcher(endpoint_url=endpoint)
    records = fetcher.fetch_records()
    logger.info("Retrieved %d financial records.", len(records))

    logger.info("Computing executive KPIs and department/quarterly aggregates...")
    processor = FinancialProcessor(records)
    kpis = processor.compute_summary_kpis()
    dept_breakdown = processor.aggregate_by_department()
    quarterly_breakdown = processor.aggregate_by_quarter()

    logger.info("Total Revenue  : %s", fmt_currency(kpis["total_revenue"]))
    logger.info("Total Expenses : %s", fmt_currency(kpis["total_expenses"]))
    logger.info("Net Profit     : %s (%s%% margin)", fmt_currency(kpis["net_profit"]), kpis["profit_margin_pct"])

    logger.info("Generating corporate PDF report at %s...", output_path)
    generator = FinancialReportGenerator(output_path=output_path)
    pdf_path = generator.build_pdf(
        kpis=kpis,
        dept_data=dept_breakdown,
        quarterly_data=quarterly_breakdown,
    )
    logger.info("Report generation completed successfully: %s", pdf_path)
    return pdf_path


def main() -> None:
    """CLI entrypoint for console script 'capstone-report'."""
    parser = argparse.ArgumentParser(
        description="RabTech Enterprise Python Automation Capstone: Financial Data Ingestion & PDF Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("reports/sample_financial_report.pdf"),
        help="Path where the generated PDF document will be stored.",
    )
    parser.add_argument(
        "--endpoint",
        "-e",
        type=str,
        default=None,
        help="Remote API endpoint URL for pulling dynamic financial records.",
    )

    args = parser.parse_args()
    try:
        pdf_file = run_pipeline(output_path=args.output, endpoint=args.endpoint)
        print(f"\n[SUCCESS] Financial report generated: {pdf_file}")
    except Exception as exc:
        logger.error("Failed to execute capstone pipeline: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
