# type: ignore

from typing import Iterator, Union, Any, Optional
from models import ChatState, VegaLiteResponse, RoutedIntent, TableSchema, ChartSuggestionResponse
from agents.router import router_agent
from agents.schema_inspector import schema_inspector
from agents.chart_suggester import chart_suggester
from agents.vega_generator import vega_generator
from agents.analytics_qna import analytics_qna


class ConversationalChartWorkflow:

    def run_agent_stream(self, agent, inputs, visible_to_user: bool = False) -> Any:
        """Streams agent output. Yields chunks. Returns the final accumulated response."""
        if isinstance(inputs, dict):
            content = str(inputs)
        else:
            content = inputs

        accumulated_text = ""
        final_object = None

        # Stream the response
        try:
            # We assume agent.run(stream=True) returns an iterator of chunks (strings or objects with content)
            stream = agent.run(content, stream=True)
            for chunk in stream:
                # Adapting to whatever Agno returns.
                # If chunk is a string (token), append to text.
                # If chunk is an object (Structured output), it might be the final result.
                
                content_item = None
                
                if isinstance(chunk, str):
                    content_item = chunk
                elif hasattr(chunk, 'content'):
                    content_item = chunk.content
                    if not isinstance(content_item, str):
                        final_object = content_item
                else:
                    # Likely a structured object (Pydantic model) directly yielded
                    final_object = chunk
                    content_item = str(chunk)

                if content_item is not None:
                     if isinstance(content_item, str):
                         accumulated_text += content_item
                     
                     if visible_to_user:
                         yield {"type": "content", "content": str(content_item)}
                     else:
                         # Stream reasoning for internal agents
                         yield {"type": "reasoning", "content": str(content_item)}
        except Exception as e:
            print(f"Error streaming agent {agent.name}: {e}")
            yield {"type": "error", "content": str(e)}
            
        # Return the best representation of the result
        if final_object:
            return final_object
        return accumulated_text

    def run(self, message: str, state: ChatState) -> Iterator[dict]:
        """
        Executes the workflow, yielding events/chunks.
        Events format: {"type": "reasoning"|"content"|"error", "content": "..."}
        """

        # 1. Router (Internal - Show reasoning)
        yield {"type": "reasoning", "content": "Analyzing request..."}
        route = yield from self.run_agent_stream(
            router_agent,
            {"message": message, "state": state}
        )
        
        # Guard: route might be string if something failed or unexpected return
        if not isinstance(route, RoutedIntent):
            # Try to handle if it's a string (unlikely given test) or just proceed safely
             yield {"type": "reasoning", "content": f"\nRouter response: {route}"}
             # If we can't determine route, fallback
             if isinstance(route, str):
                 # Simple fallback logic if it's just a string, though router should return object
                 pass

        if hasattr(route, 'table') and route.table:
            state.table = route.table
            yield {"type": "reasoning", "content": f"\nTarget table: {state.table}"}

        # ---- Suggest Charts ----
        if getattr(route, 'intent_type', None) == "suggest_charts":
            if not state.table:
                yield {"type": "content", "content": "Please specify which table you want to analyze."}
                return

            yield {"type": "reasoning", "content": "\nInspecting schema..."}
            schema = yield from self.run_agent_stream(
                schema_inspector,
                {"table": state.table}
            )

            yield {"type": "reasoning", "content": "\nGenerating suggestions..."}
            suggestions = yield from self.run_agent_stream(
                chart_suggester,
                {
                    "table": state.table,
                    "intent": message,
                    "schema": schema
                }
            )

            if isinstance(suggestions, ChartSuggestionResponse):
                state.last_suggestions = suggestions
                
                # Format suggestions as a string and yield
                formatted = "Here are some suggested charts:\n\n"
                for i, chart in enumerate(suggestions.charts, 1):
                    formatted += f"{i}. **{chart.chart_type.title()}** (ID: {chart.id})\n"
                    formatted += f"   Reason: {chart.reason}\n\n"
                
                yield {"type": "content", "content": formatted}
            else:
                yield {"type": "error", "content": "Failed to generate valid suggestions."}
            return

        # ---- Build Charts ----
        if getattr(route, 'intent_type', None) == "build_charts":
            yield {"type": "reasoning", "content": "Selected charts identified. Generating specification..."}
            selected = [
                c for c in state.last_suggestions.charts
                if c.id in route.chart_ids
            ]

            # Vega Generator (Visible output)
            # But the user asked for streaming reasoning *from agents*.
            # Vega's output IS the content. 
            # We treat it as visible content here.
            
            # Streaming accumulation is handled by run_agent_stream now
            # But we need parsing logic still.
            
            yield {"type": "reasoning", "content": "Generating Vega spec..."}
            
            # Since Vega output is the final content, we set visible_to_user=True
            chart_response_text = yield from self.run_agent_stream(
                vega_generator,
                {"table": state.table, "charts": selected},
                visible_to_user=True
            )
            
            # Parse the accumulated text to update state
            charts = chart_response_text
            # Parsing logic
            if isinstance(charts, str):
                try:
                    clean_json = charts.strip()
                    extracted_summary = None

                    if "<vega-chart>" in clean_json and "</vega-chart>" in clean_json:
                        parts = clean_json.split("</vega-chart>")
                        clean_json = parts[0].split("<vega-chart>")[1].strip()
                        if len(parts) > 1:
                            extracted_summary = parts[1].strip()
                            if extracted_summary.lower().startswith("summary:"):
                                extracted_summary = extracted_summary[8:].strip()
                                if extracted_summary.startswith('"') and extracted_summary.endswith('"'):
                                    extracted_summary = extracted_summary[1:-1]
                    
                    if clean_json.startswith("```"):
                        clean_json = clean_json.split("\n", 1)[1]
                        if clean_json.endswith("```"):
                            clean_json = clean_json.rsplit("\n", 1)[0]
                            
                    cutoff_charts = VegaLiteResponse.model_validate_json(clean_json)
                    
                    if extracted_summary and not cutoff_charts.summary:
                        cutoff_charts.summary = extracted_summary
                    
                    state.last_charts = cutoff_charts
                except Exception as e:
                    print(f"Failed to parse VegaLite response: {e}")
                    pass
            
            return

        # ---- Normal Question ----
        if getattr(route, 'intent_type', None) == "ask_question":
            yield {"type": "reasoning", "content": "Consulting data..."}
            
            yield from self.run_agent_stream(
                analytics_qna,
                {"question": route.question, "state": state},
                visible_to_user=True
            )
            return

        # ---- Clarify ----
        yield {"type": "content", "content": "Can you clarify what you want to do?"}
