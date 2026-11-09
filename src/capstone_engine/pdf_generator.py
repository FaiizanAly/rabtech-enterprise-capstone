"""Enterprise PDF Report Generator utilizing ReportLab for corporate financial documents."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def fmt_currency(value: float) -> str:
    """Format floating point numbers as standard US currency strings."""
    return f"${value:,.2f}"


class FinancialReportGenerator:
    """Generates styled enterprise financial executive reports in PDF format."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = Path(output_path)
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()

    def _init_custom_styles(self) -> None:
        """Initialize custom typographic styles."""
        self.title_style = ParagraphStyle(
            "DocTitle",
            parent=self.styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0F172A"),
            alignment=0,
            spaceAfter=4,
        )
        self.subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12,
        )
        self.heading_style = ParagraphStyle(
            "SectionHeading",
            parent=self.styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1E3A8A"),
            spaceBefore=10,
            spaceAfter=6,
        )
        self.cell_style = ParagraphStyle(
            "TableCell",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1E293B"),
        )
        self.cell_bold = ParagraphStyle(
            "TableCellBold",
            parent=self.cell_style,
            fontName="Helvetica-Bold",
        )
        self.cell_header = ParagraphStyle(
            "TableHeader",
            parent=self.cell_style,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        )

    def build_pdf(
        self,
        kpis: Dict[str, Any],
        dept_data: List[Dict[str, Any]],
        quarterly_data: List[Dict[str, Any]],
    ) -> Path:
        """Compile executive KPI metrics and tabular breakdowns into a clean PDF."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        story: List[Any] = []
        gen_time = datetime.now().strftime("%B %d, %Y - %I:%M %p")

        # 1. Header Banner
        story.append(Paragraph("RabTech Enterprise Financial & Performance Report", self.title_style))
        story.append(Paragraph(f"Fiscal Year 2026 Executive Performance Dashboard | Generated: {gen_time}", self.subtitle_style))
        story.append(Spacer(1, 8))

        # 2. Executive KPI Cards Table
        story.append(Paragraph("Executive Summary & Core Financial KPIs", self.heading_style))
        kpi_table_data = [
            [
                Paragraph("<b>Total Revenue</b>", self.cell_style),
                Paragraph(fmt_currency(kpis["total_revenue"]), self.cell_bold),
                Paragraph("<b>Total Expenses</b>", self.cell_style),
                Paragraph(fmt_currency(kpis["total_expenses"]), self.cell_bold),
            ],
            [
                Paragraph("<b>Net Profit</b>", self.cell_style),
                Paragraph(fmt_currency(kpis["net_profit"]), self.cell_bold),
                Paragraph("<b>Profit Margin</b>", self.cell_style),
                Paragraph(f"{kpis['profit_margin_pct']}%", self.cell_bold),
            ],
            [
                Paragraph("<b>Total Budget</b>", self.cell_style),
                Paragraph(fmt_currency(kpis["total_budget"]), self.cell_bold),
                Paragraph("<b>Budget Variance</b>", self.cell_style),
                Paragraph(f"{fmt_currency(kpis['budget_variance'])} (Savings)", self.cell_bold),
            ],
        ]
        kpi_table = Table(kpi_table_data, colWidths=[120, 150, 120, 150])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 14))

        # 3. Department Breakdown Table
        story.append(Paragraph("Department Financial Performance Breakdown", self.heading_style))
        dept_table_data = [
            [
                Paragraph("Department", self.cell_header),
                Paragraph("Revenue", self.cell_header),
                Paragraph("Expenses", self.cell_header),
                Paragraph("Net Profit", self.cell_header),
                Paragraph("Margin (%)", self.cell_header),
            ]
        ]
        for row in dept_data:
            dept_table_data.append([
                Paragraph(row["department"], self.cell_style),
                Paragraph(fmt_currency(row["revenue"]), self.cell_style),
                Paragraph(fmt_currency(row["expenses"]), self.cell_style),
                Paragraph(fmt_currency(row["net_profit"]), self.cell_bold),
                Paragraph(f"{row['profit_margin_pct']}%", self.cell_style),
            ])

        dept_table = Table(dept_table_data, colWidths=[160, 95, 95, 100, 90])
        dept_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(dept_table)
        story.append(Spacer(1, 14))

        # 4. Quarterly Trajectory Table
        story.append(Paragraph("Quarterly Performance Trajectory", self.heading_style))
        q_table_data = [
            [
                Paragraph("Quarter", self.cell_header),
                Paragraph("Revenue", self.cell_header),
                Paragraph("Expenses", self.cell_header),
                Paragraph("Net Profit", self.cell_header),
                Paragraph("Margin (%)", self.cell_header),
            ]
        ]
        for row in quarterly_data:
            q_table_data.append([
                Paragraph(row["quarter"], self.cell_style),
                Paragraph(fmt_currency(row["revenue"]), self.cell_style),
                Paragraph(fmt_currency(row["expenses"]), self.cell_style),
                Paragraph(fmt_currency(row["net_profit"]), self.cell_bold),
                Paragraph(f"{row['profit_margin_pct']}%", self.cell_style),
            ])

        q_table = Table(q_table_data, colWidths=[120, 105, 105, 110, 100])
        q_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0FDFA")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCFBF1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(q_table)
        story.append(Spacer(1, 14))

        # 5. Executive Observations
        story.append(Paragraph("Strategic Findings & Recommendations", self.heading_style))
        insights = [
            "• <b>AI & Automation</b> generated the highest operational profit margin, expanding by over 47% across consecutive quarters.",
            "• <b>Cloud Solutions</b> maintained strong, stable recurring revenues with an average profit margin exceeding 37%.",
            f"• Aggregate operational efficiency yielded <b>{fmt_currency(kpis['budget_variance'])}</b> in cumulative budget savings across all four fiscal quarters.",
        ]
        for insight in insights:
            story.append(Paragraph(insight, self.cell_style))
            story.append(Spacer(1, 3))

        doc.build(story)
        return self.output_path
