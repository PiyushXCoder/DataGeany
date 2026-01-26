from agno.models.google import Gemini
from backend.core.config import settings

def get_model():
    return Gemini(
        id="gemini-2.5-flash",
        temperature=0.2,
        api_key=settings.gemini_api_key
    )
