import os
from agno.models.cerebras import Cerebras
from backend.core.config import settings 
def get_agent_model():
    model = Cerebras(
        id="llama-3.1-8b",
        api_key=settings.openai_api_key
    )
    return model
