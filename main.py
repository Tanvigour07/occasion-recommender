"""FastAPI app: GET /api/recommend?occasion=Diwali, serves the single-page UI at /."""
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from recommender import Recommender
from occasions import OCCASIONS

BASE = Path(__file__).parent
app = FastAPI(title="Occasion-Based Product Recommender")
engine = Recommender(BASE / "data" / "products.json")


@app.get("/api/recommend")
def recommend(occasion: str = Query("", description="e.g. Birthday, Diwali"), limit: int = Query(12, ge=1, le=50)):
    return engine.recommend(occasion, limit)


@app.get("/api/occasions")
def occasions():
    return sorted(OCCASIONS)


app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


@app.get("/")
def index():
    return FileResponse(BASE / "static" / "index.html")
