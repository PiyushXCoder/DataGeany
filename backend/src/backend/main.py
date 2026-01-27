from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from backend.domains.items import router as items_router
from backend.domains.charts import router as charts_router


def create_app():
    app = FastAPI(
        title="DataGeany Backend",
        description="API for DataGeany application",
        version="0.0.1",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(charts_router.router, prefix="/charts", tags=["charts"])

    @app.get("/")
    async def root():
        return {"message": "Welcome to DataGeany API"}

    return app

app = create_app()

def main():
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
