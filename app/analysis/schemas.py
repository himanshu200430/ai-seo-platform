from datetime import datetime
from typing import Literal

from pydantic import BaseModel

class Issue(BaseModel):
    issue_id: str
    website: str
    page_url: str
    issue_type: str
    supporting_metrics: dict[str, float]
    comparison_period: str
    severity: Literal["low", "medium", "high"]
    confidence: Literal["low", "medium", "high"]
    detected_at: datetime
    suggested_next_investigation: str