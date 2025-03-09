import json
from pydantic import BaseModel

from app.services.db_service import get_schedule_2, get_different_buildings_2, get_long_breaks_2, \
    get_short_breaks_different_campus_2
from app.models.request_status import RequestStatus
from app.services.schedule_service import get_schedule, get_different_buildings, get_long_breaks, \
    get_short_breaks_different_campus
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.background_service import process_request

app = FastAPI()


# level 1
@app.get("/schedule_1")
async def schedule_endpoint(query: str = None):
    return await get_schedule(query)


@app.get("/different-buildings_1")
async def different_buildings_endpoint(query: str = None):
    return await get_different_buildings(query)


@app.get("/long-breaks_1")
async def long_breaks_endpoint(query: str = None):
    return await get_long_breaks(query)


@app.get("/short-breaks-different-campus_1")
async def short_breaks_different_campus_endpoint(query: str = None):
    return await get_short_breaks_different_campus(query)


# level_2
@app.get("/schedule_2")
async def schedule_endpoint(query: str = None, db: Session = Depends(get_db)):
    return await get_schedule_2(query, db)


@app.get("/different-buildings_2")
async def different_buildings_endpoint(query: str = None, db: Session = Depends(get_db)):
    return await get_different_buildings_2(query, db)


@app.get("/long-breaks_2")
async def long_breaks_endpoint(query: str = None, db: Session = Depends(get_db)):
    return await get_long_breaks_2(query, db)


@app.get("/short-breaks-different-campus_2")
async def short_breaks_different_campus_endpoint(query: str = None, db: Session = Depends(get_db)):
    return await get_short_breaks_different_campus_2(query, db)


class RequestCreate(BaseModel):
    query: str


# level 3
@app.post("/schedule_3")
async def schedule_endpoint(request: RequestCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Создает новый запрос и запускает обработку в фоне."""
    request_status = RequestStatus(query_text=request.query, status="in_progress")
    db.add(request_status)
    db.commit()
    db.refresh(request_status)

    # Запускаем фоновую задачу
    background_tasks.add_task(process_request, request.query, request_status.id, "schedule")

    return {"request_id": request_status.id}


@app.post("/different-buildings_3")
async def different_buildings_endpoint(request: RequestCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Создает новый запрос для разных зданий и запускает обработку в фоне."""
    request_status = RequestStatus(query_text=request.query, status="in_progress")
    db.add(request_status)
    db.commit()
    db.refresh(request_status)

    # Запускаем фоновую задачу
    background_tasks.add_task(process_request, request.query, request_status.id, "different-buildings")

    return {"request_id": request_status.id}


@app.post("/long-breaks_3")
async def long_breaks_endpoint(request: RequestCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Создает новый запрос для длинных перерывов и запускает обработку в фоне."""
    request_status = RequestStatus(query_text=request.query, status="in_progress")
    db.add(request_status)
    db.commit()
    db.refresh(request_status)

    # Запускаем фоновую задачу
    background_tasks.add_task(process_request, request.query, request_status.id, "long-breaks")

    return {"request_id": request_status.id}


@app.post("/short-breaks-different-campus_3")
async def short_breaks_different_campus_endpoint(request: RequestCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Создает новый запрос для коротких перерывов на разных кампусах и запускает обработку в фоне."""
    request_status = RequestStatus(query_text=request.query, status="in_progress")
    db.add(request_status)
    db.commit()
    db.refresh(request_status)

    # Запускаем фоновую задачу
    background_tasks.add_task(process_request, request.query, request_status.id, "short-breaks-different-campus")

    return {"request_id": request_status.id}


@app.get("/status/{request_id}")
async def get_request_status(request_id: int, db: Session = Depends(get_db)):
    """Возвращает статус и результат запроса."""
    request_status = db.query(RequestStatus).filter(RequestStatus.id == request_id).first()
    if not request_status:
        raise HTTPException(status_code=404, detail="Request not found")

    return {
        "status": request_status.status,
        "result": json.loads(request_status.result) if request_status.status == "completed" else None
    }
