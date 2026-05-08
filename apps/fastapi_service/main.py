from fastapi import FastAPI

app = FastAPI(title="Video Processing Service")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "FastAPI service is running"}