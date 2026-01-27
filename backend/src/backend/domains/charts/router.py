from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from typing import List, Dict, Any
from .schemas import ChartSuggestionRequest
from ...shared.ai_agents.agents.chart_suggester_agent import agent as suggest_agent
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
    try:
        file_path = service.get_csv_path(csv_id)
        return FileResponse(file_path, media_type="text/csv", filename=f"{csv_id}.csv")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CSV not found")

@router.get("/csv/{csv_id}/schema")
async def get_csv_schema(csv_id: str):
    try:
        schema = service.get_csv_schema(csv_id)
        return {"csvId": csv_id, "schema": schema}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CSV not found")

