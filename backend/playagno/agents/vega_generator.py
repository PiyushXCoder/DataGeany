from agno.agent import Agent
from agno.tools.sql import SQLTools
from models import VegaLiteResponse
from backend.shared.database.manager import get_db 
from utils import get_agent_model

vega_generator = Agent(
    name="VegaLiteGeneratorAgent",
    model=get_agent_model(),
    instructions="""
Generate Vega-Lite v5 specifications.
Uset table name to generate chart.

Rules:
- One Vega-Lite spec per chart
- Use aggregation when provided
- Assume data comes from a SQL table
- Keep specs minimal and valid

Return JSON only matching this structure:
{
    "table": "table_name",
    "charts": [
        {
            "id": "chart_id",
            "title": "Chart Title",
            "description": "Chart Description",
            "spec": { ... vega-lite spec ... }
        }
    ],
    "summary": "Brief summary of what was generated"
}
""",
    tools=[SQLTools(db_engine=get_db().engine)],
)
