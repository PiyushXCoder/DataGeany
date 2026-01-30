from agno.agent import Agent
from models import ChartSuggestionResponse
from utils import get_agent_model

chart_suggester = Agent(
    name="ChartSuggesterAgent",
    model=get_agent_model(),
    instructions="""
You are a data visualization expert.

Given:
- table name
- table schema
- user intent

Suggest multiple appropriate charts.
Assign unique IDs like chart_1, chart_2, etc.
Only suggest charts that are feasible from the schema.

Return JSON only.
""",
    output_schema=ChartSuggestionResponse,
)
