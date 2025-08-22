"""Alternative entry point for the FastAPI application."""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    from app.config import config
    
    uvicorn.run(
        "app.main:app",
        host=config.get("app.host", "0.0.0.0"),
        port=config.get("app.port", 8000),
        reload=config.get("app.debug", True)
    )