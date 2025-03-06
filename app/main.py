from fastapi import FastAPI

from app.database import add_history, add_group, HistoryHasGroup, add_event, add_long_break, add_short_break, \
    add_different_building, SessionLocal
from app.services.schedule_service import get_schedule, get_different_buildings, get_long_breaks, get_short_breaks_different_campus
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/schedule")
async def schedule_endpoint(query: str = None, db: Session = Depends(get_db)):
    response = await get_schedule(query)

    # Сохраняем историю запроса
    history = add_history(db, query)

    # Сохраняем группы и связываем их с историей
    for calname, events in response['events_by_calname'].items():
        group = add_group(db, calname)
        history_group = HistoryHasGroup(history_id=history.id, group_id=group.id)
        db.add(history_group)
        db.commit()

        # Сохраняем события
        for event in events:
            add_event(db, event, group.id)

        # Сохраняем длинные перерывы
        for long_break in response['long_breaks']:
            add_long_break(db, long_break, group.id)

        # Сохраняем короткие перерывы
        for short_break in response['short_breaks_different_campus']:
            add_short_break(db, short_break, group.id)

        # Сохраняем разные здания
        for different_building in response['different_buildings']:
            add_different_building(db, different_building, group.id)

    return response


@app.get("/different-buildings")
async def different_buildings_endpoint(query: str = None):
    return await get_different_buildings(query)


@app.get("/long-breaks")
async def long_breaks_endpoint(query: str = None):
    return await get_long_breaks(query)


@app.get("/short-breaks-different-campus")
async def short_breaks_different_campus_endpoint(query: str = None):
    return await get_short_breaks_different_campus(query)
