from agno.agent import Agent
from ..core.agno_sdk_init import get_model
from typing import Literal
from pydantic import BaseModel, Field

class XAxis(BaseModel):
    column: str = Field(..., description="Categorical column name")
    label: str = Field(..., description="X-axis label")

class YAxis(BaseModel):
    column: str = Field(..., description="Numeric column name")
    aggregation: Literal["sum", "avg", "count"] = Field(
        ..., description="Aggregation method"
    )
    label: str = Field(..., description="Y-axis label")

class BarChartPlan(BaseModel):
    type: Literal["bar"] = Field("bar", description="Chart type")
    x: XAxis
    y: YAxis
    top_k: int = Field(10, ge=1, le=50, description="Top K categories")


def agent():
    return Agent(
        name="ChartSuggesterAgent",
        model=get_model(),
        tools=[],
        output_schema=BarChartPlan,
        instructions="""
You are a data visualization planner.

You receive:
- CSV schema
- User intent

Your job:
- Choose suitable columns for a BAR chart
- Choose aggregation logic
- NEVER generate numeric data
- Return JSON matching the provided schema
        """
    )
