from agno.agent import Agent
from pydantic import BaseModel, Field
from ..core.agno_sdk_init import get_model

class ResponseModel(BaseModel):
    chart_types: list[str] = Field(default=[], description="The suggested chart type to visualize the data effectively.")

def agent():
    return Agent(
        name="ChartSuggesterAgent",
        model=get_model(),
        tools=[],
        output_schema=ResponseModel,
        instructions="""
        You are a backend chart-suggesting agent.
        User is using a csv file to visualize data. He will tell about columns, data types and insights he wants to derive in json.
        Based on the user's request, suggest the most appropriate chart type (e.g., bar chart, line chart, pie chart, scatter plot, etc.) to visualize the data effectively.
        Consider the nature of the data and the insights the user wants to derive when making your suggestion. 
        """
    )
