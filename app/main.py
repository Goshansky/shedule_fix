from fastapi import FastAPI
from app.services.schedule_service import get_schedule, get_different_buildings, get_long_breaks, get_short_breaks_different_campus

app = FastAPI()

@app.get("/schedule")
async def schedule_endpoint(query: str = None):
    return await get_schedule(query)

@app.get("/different-buildings")
async def different_buildings_endpoint(query: str = None):
    return await get_different_buildings(query)

@app.get("/long-breaks")
async def long_breaks_endpoint(query: str = None):
    return await get_long_breaks(query)

@app.get("/short-breaks-different-campus")
async def short_breaks_different_campus_endpoint(query: str = None):
    return await get_short_breaks_different_campus(query)
