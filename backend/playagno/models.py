from pydantic import BaseModel
from typing import List, Optional, Literal


# -------- Schema --------
class ColumnInfo(BaseModel):
    name: str
    type: str


class TableSchema(BaseModel):
    table: str
    columns: List[ColumnInfo]


# -------- Chart Suggestion --------
class ChartSuggestion(BaseModel):
    id: str
    chart_type: Literal[
        "bar", "line", "area", "pie",
        "scatter", "histogram"
    ]
    x: str
    y: Optional[str]
    aggregation: Optional[str]
    reason: str


class ChartSuggestionResponse(BaseModel):
    table: str
    intent: str
    charts: List[ChartSuggestion]


# -------- Vega Lite --------
class VegaLiteChart(BaseModel):
    id: str
    title: str
    description: str
    spec: dict


class VegaLiteResponse(BaseModel):
    table: str
    charts: List[VegaLiteChart]
    summary: Optional[str] = None


# -------- Routing --------
IntentType = Literal[
    "suggest_charts",
    "build_charts",
    "ask_question",
    "clarify"
]


class RoutedIntent(BaseModel):
    intent_type: IntentType
    table: Optional[str]
    chart_ids: Optional[List[str]]
    question: Optional[str]


# -------- Chat State --------
class ChatState(BaseModel):
    table: Optional[str] = None
    last_suggestions: Optional[ChartSuggestionResponse] = None
    last_charts: Optional[VegaLiteResponse] = None
