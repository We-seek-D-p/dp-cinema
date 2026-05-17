from api.v1.api import api_router
from fastapi import FastAPI

app = FastAPI(title="Video Processing Service")
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "FastAPI service is running"}
