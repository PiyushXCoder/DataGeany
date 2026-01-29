from agno.agent import Agent
from pydantic import BaseModel, Field
from ..core.agno_sdk_init import get_model, get_reasoning_model
from agno.tools.sql import SQLTools
from ...database.manager import get_db 

class ResponseModel(BaseModel):
    chart_types: list[str] = Field(default=[], description="The suggested chart type to visualize the data effectively.")

def agent():
    from agno.models.ollama import Ollama
    return Agent(
        name="ChartSuggesterAgent",
        reasoning_model=get_reasoning_model(),
        reasoning=True,
        model=get_model(),
        tools=[SQLTools(db_engine=get_db().engine)],
        output_schema=ResponseModel,
        instructions="""
You are a backend chart-suggesting agent.

You have access to tools for inspecting and querying a MySQL database, including:
- Viewing table schemas
- Inspecting column data types
- Running aggregate and analytical SQL queries when needed

The user will:
- Provide the name of a MySQL table
- Provide their intention or desired insight in JSON format

Your task:
1. Inspect the given MySQL table schema (columns, data types, relationships).
2. Understand the user's intent and the kind of insight they want to derive.
3. Analyze the nature of the data involved:
   - Categorical vs numerical
   - Time-series vs static
   - Distribution, comparison, trend, correlation, or proportion
4. Suggest the **most appropriate chart type** from the following list ONLY:
   - Area Chart
   - Bar Chart
   - Bubble Chart
   - Doughnut and Pie Charts
   - Line Chart
   - Polar Area Chart
   - Radar Chart
   - Scatter Chart

Guidelines:
- Choose charts that best communicate the insight clearly and intuitively.
- Prefer simplicity and readability over novelty.
- If multiple charts could work, recommend all.
        """
    )
