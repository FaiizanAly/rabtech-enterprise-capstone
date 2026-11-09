"""Business Intelligence and financial metric aggregation processor."""

from typing import Any, Dict, List


class FinancialProcessor:
    """Processes raw financial records into executive KPIs, department analytics, and summary tables."""

    def __init__(self, records: List[Dict[str, Any]]) -> None:
        if not records:
            raise ValueError("Records list cannot be empty.")
        self.records = records

    def compute_summary_kpis(self) -> Dict[str, Any]:
        """Aggregate total revenue, expenses, net profit, and profit margin."""
        total_rev = sum(float(r["revenue"]) for r in self.records)
        total_exp = sum(float(r["expenses"]) for r in self.records)
        total_budget = sum(float(r.get("budget", r["expenses"])) for r in self.records)
        net_profit = total_rev - total_exp
        profit_margin = (net_profit / total_rev * 100) if total_rev > 0 else 0.0
        budget_variance = total_budget - total_exp  # Positive means under-budget savings

        return {
            "total_revenue": round(total_rev, 2),
            "total_expenses": round(total_exp, 2),
            "net_profit": round(net_profit, 2),
            "profit_margin_pct": round(profit_margin, 2),
            "total_budget": round(total_budget, 2),
            "budget_variance": round(budget_variance, 2),
            "record_count": len(self.records),
        }

    def aggregate_by_department(self) -> List[Dict[str, Any]]:
        """Compute aggregate performance breakdown by department."""
        dept_data: Dict[str, Dict[str, float]] = {}
        for r in self.records:
            dept = str(r["department"])
            if dept not in dept_data:
                dept_data[dept] = {"revenue": 0.0, "expenses": 0.0, "budget": 0.0}
            dept_data[dept]["revenue"] += float(r["revenue"])
            dept_data[dept]["expenses"] += float(r["expenses"])
            dept_data[dept]["budget"] += float(r.get("budget", r["expenses"]))

        summary: List[Dict[str, Any]] = []
        for dept, vals in sorted(dept_data.items()):
            net = vals["revenue"] - vals["expenses"]
            margin = (net / vals["revenue"] * 100) if vals["revenue"] > 0 else 0.0
            summary.append({
                "department": dept,
                "revenue": round(vals["revenue"], 2),
                "expenses": round(vals["expenses"], 2),
                "net_profit": round(net, 2),
                "profit_margin_pct": round(margin, 2),
            })
        return summary

    def aggregate_by_quarter(self) -> List[Dict[str, Any]]:
        """Compute aggregate performance breakdown by quarter."""
        q_data: Dict[str, Dict[str, float]] = {}
        for r in self.records:
            q = str(r["quarter"])
            if q not in q_data:
                q_data[q] = {"revenue": 0.0, "expenses": 0.0}
            q_data[q]["revenue"] += float(r["revenue"])
            q_data[q]["expenses"] += float(r["expenses"])

        summary: List[Dict[str, Any]] = []
        for q, vals in q_data.items():
            net = vals["revenue"] - vals["expenses"]
            margin = (net / vals["revenue"] * 100) if vals["revenue"] > 0 else 0.0
            summary.append({
                "quarter": q,
                "revenue": round(vals["revenue"], 2),
                "expenses": round(vals["expenses"], 2),
                "net_profit": round(net, 2),
                "profit_margin_pct": round(margin, 2),
            })
        return summary
