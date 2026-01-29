from pydantic import BaseModel
from typing import Dict, Optional

class PlanChartRequest(BaseModel):
    chart_type: str
    columns: Dict[str, str]
    user_query: str
