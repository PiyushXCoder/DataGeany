from fastapi import FastAPI

from backend.domains.items import router as items_router


def create_app():
    app = FastAPI(
        title="DataGeany Backend",
        description="API for DataGeany application",
        version="0.0.1",
    )

    app.include_router(items_router.router, prefix="/items", tags=["items"])

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
