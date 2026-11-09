"""Enterprise data fetcher with resilient HTTP requests and fallback sample generation."""

import logging
from typing import Any, Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

DEFAULT_ENTERPRISE_DATA: List[Dict[str, Any]] = [
    {"quarter": "Q1 2026", "department": "Cloud Solutions", "revenue": 1250000.00, "expenses": 820000.00, "budget": 850000.00},
    {"quarter": "Q1 2026", "department": "Data Engineering", "revenue": 980000.00, "expenses": 610000.00, "budget": 650000.00},
    {"quarter": "Q1 2026", "department": "AI & Automation", "revenue": 1420000.00, "expenses": 890000.00, "budget": 900000.00},
    {"quarter": "Q2 2026", "department": "Cloud Solutions", "revenue": 1380000.00, "expenses": 860000.00, "budget": 880000.00},
    {"quarter": "Q2 2026", "department": "Data Engineering", "revenue": 1050000.00, "expenses": 630000.00, "budget": 660000.00},
    {"quarter": "Q2 2026", "department": "AI & Automation", "revenue": 1650000.00, "expenses": 940000.00, "budget": 950000.00},
    {"quarter": "Q3 2026", "department": "Cloud Solutions", "revenue": 1450000.00, "expenses": 890000.00, "budget": 900000.00},
    {"quarter": "Q3 2026", "department": "Data Engineering", "revenue": 1120000.00, "expenses": 670000.00, "budget": 690000.00},
    {"quarter": "Q3 2026", "department": "AI & Automation", "revenue": 1820000.00, "expenses": 1010000.00, "budget": 1020000.00},
    {"quarter": "Q4 2026", "department": "Cloud Solutions", "revenue": 1620000.00, "expenses": 950000.00, "budget": 980000.00},
    {"quarter": "Q4 2026", "department": "Data Engineering", "revenue": 1280000.00, "expenses": 720000.00, "budget": 740000.00},
    {"quarter": "Q4 2026", "department": "AI & Automation", "revenue": 2100000.00, "expenses": 1150000.00, "budget": 1180000.00},
]


class FinancialDataFetcher:
    """Fetches quarterly financial and operational records from API with safe fallback."""

    def __init__(self, endpoint_url: Optional[str] = None, timeout: float = 5.0) -> None:
        self.endpoint_url = endpoint_url
        self.timeout = timeout

    def fetch_records(self) -> List[Dict[str, Any]]:
        """Fetch records from remote API, falling back to curated enterprise dataset if unavailable."""
        if self.endpoint_url:
            try:
                response = requests.get(
                    self.endpoint_url,
                    headers={"User-Agent": "RabTech-Capstone-Engine/1.0", "Accept": "application/json"},
                    timeout=self.timeout,
                )
                if response.status_code == 200:
                    payload = response.json()
                    if isinstance(payload, list) and len(payload) > 0:
                        return payload
                    if isinstance(payload, dict) and "records" in payload:
                        return payload["records"]
                logger.warning("Remote endpoint returned status %d. Falling back to default data.", response.status_code)
            except (requests.RequestException, Exception) as exc:
                logger.warning("Network request to %s failed: %s. Using default data.", self.endpoint_url, exc)

        return [record.copy() for record in DEFAULT_ENTERPRISE_DATA]
