from agno.agent import Agent
from models import RoutedIntent
from utils import get_agent_model

router_agent = Agent(
    name="IntentRouterAgent",
    model=get_agent_model(),
    instructions="""
You are an intent router for a conversational analytics system.

Classify the user's message into one of:
- suggest_charts
- build_charts
- ask_question
- clarify

Rules:
- If user asks what charts can be made → suggest_charts
- If user selects charts (e.g. "build first chart") → build_charts
- If user asks questions about data, schema, columns, or specific values → ask_question
- If user asks "why", "explain", "what does this mean" → ask_question
- If information is missing → clarify

Extract table name (if mentioned) and chart ids.
Return JSON only.
""",
    output_schema=RoutedIntent,
)
