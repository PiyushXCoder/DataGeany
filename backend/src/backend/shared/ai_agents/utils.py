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
        
        # 1. Reasoning
        if hasattr(chunk, "reasoning_content") and chunk.reasoning_content:
            yield f"event: reasoning\ndata: {chunk.reasoning_content}\n\n"
        
        # 2. Reasoning Delta
        if event_type == RunEvent.reasoning_content_delta:
                if hasattr(chunk, "reasoning_content") and chunk.reasoning_content:
                    yield f"event: reasoning\ndata: {chunk.reasoning_content}\n\n"
                continue # Handled

        # 3. Content (RunOutput or RunContent)
        if hasattr(chunk, "content") and chunk.content is not None:
            # RunOutput often validates to ResponseModel
            if isinstance(chunk, RunOutput) or event_type == RunEvent.run_content:
                    if hasattr(chunk.content, "model_dump_json"):
                        yield f"event: content\ndata: {chunk.content.model_dump_json()}\n\n"
                        continue
                    elif isinstance(chunk.content, str):
                        yield f"event: content\ndata: {chunk.content}\n\n"
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
                # Avoid duplicate content from RunCompleted (it duplicates RunContent or the stream)
                if event_type == "RunCompleted" or event_type == RunEvent.run_completed:
                    pass # We still emit the event metadata below, but might want to handle it carefully. 
                         # Actually, the previous logic skipped it entirely to avoid content duplication.
                         # Let's emit the metadata but be careful not to confuse the client with 'content' field if we already sent it.
                         # However, for generic handling, we usually want the metadata.
                         # The prompt "all events are not yet handled" implies valid metadata events should be sent.
                         # But let's stick to the previous successfully verified logic:
                         # The previous logic skipped RunCompleted to avoid *duplicate content*.
                         # But `RunCompleted` event itself is useful (metrics etc).
                         # Let's emit it as 'runcompleted' event.

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
