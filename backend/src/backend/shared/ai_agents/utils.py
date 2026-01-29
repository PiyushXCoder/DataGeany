from typing import Iterator
import json
from agno.agent import RunEvent, RunOutput, RunOutputEvent

def generate_sse_events(stream: Iterator[RunOutputEvent | RunOutput]):
    """
    Generates Server-Sent Events (SSE) from an Agno agent stream.
    
    Handles:
    - distinct 'reasoning' events
    - 'content' events with Pydantic serialization support
    - generic lifecycle events (e.g. runstarted, modelrequeststarted)
    """
    for chunk in stream:
        event_type = getattr(chunk, "event", None)
        
        # --- Special Handling for Reasoning & Content ---
        
        # 1. Reasoning Steps (the actual reasoning is here, not in reasoning_content)
        if hasattr(chunk, "reasoning_steps") and chunk.reasoning_steps:
            # reasoning_steps is a list of ReasoningStep objects
            # Each ReasoningStep has a 'result' field with the reasoning content
            reasoning_texts = []
            for step in chunk.reasoning_steps:
                if hasattr(step, 'result') and step.result:
                    reasoning_texts.append(step.result)
            
            if reasoning_texts:
                combined_reasoning = "\n".join(reasoning_texts)
                yield f"event: reasoning\ndata: {json.dumps({'content': combined_reasoning})}\n\n"
        
        # 2. Reasoning Content (fallback, might be used in some models)
        elif hasattr(chunk, "reasoning_content") and chunk.reasoning_content:
            yield f"event: reasoning\ndata: {json.dumps({'content': chunk.reasoning_content})}\n\n"
        
        # 3. Regular Content (RunOutput or RunContent)
        if hasattr(chunk, "content") and chunk.content is not None:
            # RunOutput often validates to ResponseModel
            if isinstance(chunk, RunOutput) or event_type == RunEvent.run_content:
                    if hasattr(chunk.content, "model_dump_json"):
                        yield f"event: content\ndata: {chunk.content.model_dump_json()}\n\n"
                        continue
                    elif isinstance(chunk.content, str):
                        yield f"event: content\ndata: {json.dumps({'content': chunk.content})}\n\n"
                        continue
                    else:
                        try:
                            yield f"event: content\ndata: {json.dumps(chunk.content)}\n\n"
                            continue
                        except TypeError:
                            pass
        
        # --- Generic Handling for ALL other events ---
        # Emit everything else as an event with its name (converted to snake_case if needed)
        if event_type:
                safe_event_name = str(event_type).replace("RunEvent.", "").lower()
        
                # Serialize the whole chunk metadata
                try:
                    if hasattr(chunk, "model_dump_json"):
                        data = chunk.model_dump_json()
                    elif hasattr(chunk, "__dict__"):
                        data = json.dumps(vars(chunk), default=str)
                    else:
                        data = str(chunk)
        
                    yield f"event: {safe_event_name}\ndata: {data}\n\n"
                except Exception as e:
                    # In a production util, maybe log this.
                    pass
