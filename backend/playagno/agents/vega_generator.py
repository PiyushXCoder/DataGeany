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
Use table name to generate chart.

Rules:
- One Vega-Lite spec per chart
- Use aggregation when provided
- ALWAYS run a SQL query to get the data for the chart.
- Embed the result data directly into the "data" field of the Vega-Lite spec using "values": [ ... ].
- Do NOT use "url" in the "data" field.
- Limit the data to 50 rows if the dataset is large.
- Keep specs minimal and valid
- If SQL fails or table doesn't exist, return empty "values": [] and explain in "summary".
- Output MUST be valid JSON wrapped in `<vega-chart>` and `</vega-chart>` tags.
- The JSON inside the tags must be strictly valid JSON.
- Surround the ENTIRE JSON object with `<vega-chart>` and `</vega-chart>`.
- Provide a summary of the chart generated OUTSIDE the tags.

Example Output:
<vega-chart>
{
    "table": "table_name",
    "charts": [...]
}
</vega-chart>
Summary: "Brief summary what can be inferred from the chart"

Return JSON matching this structure (wrapped in tags):
{
    "table": "table_name",
    "charts": [
        {
            "id": "chart_id",
            "title": "Chart Title",
            "description": "Chart Description",
            "spec": { ... vega-lite spec ... }
        }
    ]
}
Summary: "Brief summary what can be inferred from the chart"
""",
    tools=[SQLTools(db_engine=get_db().engine)],
)
