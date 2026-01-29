from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from typing import List, Dict, Any
from .schemas import ChartSuggestionRequest, PlanChartRequest
from ...shared.ai_agents.agents.chart_suggester_agent import agent as suggest_agent
from ...shared.ai_agents.agents.bar_chart_agent import agent as bar_chart_agent
from ...shared.ai_agents.utils import generate_sse_events
from .service import ChartService

router = APIRouter()
service = ChartService()

@router.post("/suggest")
async def suggest_charts(request: ChartSuggestionRequest):
    chart_agent = suggest_agent()
    
    stream = chart_agent.run(
        f"Columns: {request.columns}\nUser Query: {request.user_query}", 
        stream=True
    )

    return StreamingResponse(
        generate_sse_events(stream),
        media_type="text/event-stream"
    )

@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        csv_id = service.upload_csv(file)
        return {"status": "success", "message": "CSV uploaded", "csvId": csv_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/csv/{csv_id}")
async def get_csv_data(csv_id: str):
    """Get CSV data from the database table."""
    try:
        from ...shared.database import CSVStorage
        data = CSVStorage.get_table_data(csv_id, limit=10000)
        return {"csvId": csv_id, "data": data}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"CSV data not found: {str(e)}")

@router.get("/csv/{csv_id}/head")
async def get_csv_head(csv_id: str):
    """Get the first 5 rows of CSV data from the database table."""
    try:
        from ...shared.database import CSVStorage
        data = CSVStorage.get_table_data(csv_id, limit=5)
        return {"csvId": csv_id, "data": data}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"CSV data not found: {str(e)}")

@router.get("/csv/{csv_id}/schema")
async def get_csv_schema(csv_id: str):
    try:
        schema = service.get_csv_schema(csv_id)
        return {"csvId": csv_id, "schema": schema}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CSV not found")

@router.post("/plan_chart")
async def plan_chart(request: PlanChartRequest):
    if request.chart_type == "bar":
        agent = bar_chart_agent()
        stream = agent.run(
            f"Columns: {request.columns}\nUser Query: {request.user_query}",
            stream=True
        )
        return StreamingResponse(
            generate_sse_events(stream),
            media_type="text/event-stream"
        )
    
    raise HTTPException(status_code=400, detail="Unsupported chart type")
