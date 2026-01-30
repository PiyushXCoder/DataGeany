from agno.agent import Agent
from agno.tools.sql import SQLTools
from backend.shared.database.manager import get_db

from utils import get_agent_model

analytics_qna = Agent(
    name="AnalyticsQnAAgent",
    model=get_agent_model(),
    tools=[SQLTools(db_engine=get_db().engine)],
    instructions="""
You are a data analyst.

Answer the user's question using:
- The SQL table
- Suggested charts
- Generated charts (if any)

If exact data is unknown, reason conceptually.
Be concise and analytical.
""",
)
