from pydantic import BaseModel
from typing import Dict, Optional

class ChartSuggestionRequest(BaseModel):
    columns: Dict[str, str]
    user_query: str
    csv_id: Optional[str] = None
