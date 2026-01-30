from agno.workflow import Workflow
from models import ChatState, VegaLiteResponse
from agents.router import router_agent
from agents.schema_inspector import schema_inspector
from agents.chart_suggester import chart_suggester
from agents.vega_generator import vega_generator
from agents.analytics_qna import analytics_qna


class ConversationalChartWorkflow(Workflow):

    def run_agent(self, agent, inputs):
        # Convert dictionary inputs to string to avoid Message validation errors
        # (Agno might try to parse dicts as Message objects)
        if isinstance(inputs, dict):
            content = str(inputs)
        else:
            content = inputs
            
        response = agent.run(content)
        return response.content

    def run(self, message: str, state: ChatState):

        route = self.run_agent(
            router_agent,
            {"message": message, "state": state}
        )

        if route.table:
            state.table = route.table

        # ---- Suggest Charts ----
        if route.intent_type == "suggest_charts":
            if not state.table:
                return "Please specify which table you want to analyze.", state

            schema = self.run_agent(
                schema_inspector,
                {"table": state.table}
            )

            suggestions = self.run_agent(
                chart_suggester,
                {
                    "table": state.table,
                    "intent": message,
                    "schema": schema
                }
            )

            state.last_suggestions = suggestions
            return suggestions, state

        # ---- Build Charts ----
        if route.intent_type == "build_charts":
            selected = [
                c for c in state.last_suggestions.charts
                if c.id in route.chart_ids
            ]

            charts = self.run_agent(
                vega_generator,
                {
                    "table": state.table,
                    "charts": selected
                }
            )

            # Parse JSON if response is a string
            if isinstance(charts, str):
                try:
                    # Strip markdown code blocks if present
                    clean_json = charts.strip()
                    if clean_json.startswith("```"):
                        clean_json = clean_json.split("\n", 1)[1]
                        if clean_json.endswith("```"):
                            clean_json = clean_json.rsplit("\n", 1)[0]
                    charts = VegaLiteResponse.model_validate_json(clean_json)
                except Exception as e:
                    print(f"Failed to parse VegaLite response: {e}")
                    # Keep as string or handle error? 
                    # State expects VegaLiteResponse, so we might need fallback or let it crash gracefully
                    pass

            state.last_charts = charts
            return charts, state

        # ---- Normal Question ----
        if route.intent_type == "ask_question":
            answer = self.run_agent(
                analytics_qna,
                {
                    "question": route.question,
                    "state": state
                }
            )
            return answer, state

        # ---- Clarify ----
        return "Can you clarify what you want to do?", state
