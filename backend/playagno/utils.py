import os
from agno.models.cerebras import Cerebras
from agno.models.openai import OpenAIChat
from backend.core.config import settings 
def get_agent_model():
    model = Cerebras(
        id="llama-3.3-70b",
        api_key=settings.openai_api_key,
    )
    return model
