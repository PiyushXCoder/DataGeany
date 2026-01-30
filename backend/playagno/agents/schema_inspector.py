from agno.agent import Agent
from agno.tools.sql import SQLTools
from models import TableSchema
from backend.shared.database.manager import get_db 
from utils import get_agent_model

schema_inspector = Agent(
    name="SchemaInspectorAgent",
    model=get_agent_model(),
    tools=[SQLTools(db_engine=get_db().engine)],
    instructions="""
Given a SQL table name, inspect its schema.
Return column names and types.
""",
)
