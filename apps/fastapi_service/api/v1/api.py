from fastapi import APIRouter

from .movies_process import router as movies_router

api_router = APIRouter()
api_router.include_router(movies_router, prefix="/internal/movies", tags=["movies"])
