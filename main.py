import uvicorn
from fastapi_app.main import app

# Export app for ASGI servers like uvicorn main:app
__all__ = ["app"]

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
