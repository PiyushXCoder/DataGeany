from backend.core.config import settings

def get_model():
    if settings.llm == "gemini":
        from agno.models.google import Gemini
        return Gemini(
            id="gemini-2.5-flash",
            temperature=0.2,
            api_key=settings.gemini_api_key
        )
    elif settings.llm == "qwen3":
        from agno.models.ollama import Ollama 
        return Ollama(
            id="qwen3:14b",
            host=settings.ollama_host,
        )
    elif settings.llm == "deepseek":
        from agno.models.ollama import Ollama 
        return Ollama(
            id="llama3.1:8b",
            host=settings.ollama_host,
        )
    else:
        raise ValueError(f"Unsupported LLM: {settings.llm}")


def get_reasoning_model():
    if settings.llm == "deepseek":
        from agno.models.ollama import Ollama 
        return Ollama(
            id="deepseek-r1:1.5b",
            host=settings.ollama_host,
        )
    else:
        raise ValueError(f"Unsupported LLM: {settings.llm}")
