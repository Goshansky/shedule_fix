import json
from pydantic import BaseModel
from datetime import datetime

from app.database import add_history, add_group, HistoryHasGroup, add_event, add_long_break, add_short_break, \
    add_different_building, SessionLocal, Group, get_history_by_text, get_events_by_group_id, \
    get_long_breaks_by_group_id, \
    get_short_breaks_by_group_id, get_different_buildings_by_group_id, get_events_lb_by_long_break_id, \
    get_events_sb_by_short_break_id, get_events_db_by_different_building_id, RequestStatus
from app.services.schedule_service import get_schedule, get_different_buildings, get_long_breaks, \
    get_short_breaks_different_campus
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    # Проверяем, был ли выполнен такой запрос ранее
    history = get_history_by_text(db, query)
    if history:
        # Возвращаем данные из базы данных
        group_has_histories = db.query(HistoryHasGroup).filter(HistoryHasGroup.history_id == history.id).all()
        response = []
        for ghh in group_has_histories:
            group = db.query(Group).filter(Group.id == ghh.group_id).first()
            events = get_events_by_group_id(db, group.id)
            long_breaks = get_long_breaks_by_group_id(db, group.id)
            short_breaks = get_short_breaks_by_group_id(db, group.id)
            different_buildings = get_different_buildings_by_group_id(db, group.id)

            # Добавляем вложенные события
            for long_break in long_breaks:
                long_break.events = get_events_lb_by_long_break_id(db, long_break.id)

            for short_break in short_breaks:
                short_break.events = get_events_sb_by_short_break_id(db, short_break.id)

            for different_building in different_buildings:
                different_building.events = get_events_db_by_different_building_id(db, different_building.id)

            response.append({
                "events_by_calname": {group.name: [event.to_dict() for event in events]},
                "different_buildings": [
                    {
                        "day": db.day,
                        "week_parity": db.week_parity,
                        "buildings": list(set(event.location[event.location.find("(") + 1:-1] for event in db.events)),
                        "events_by_building": [{list(set(event.location[event.location.find("(") + 1:-1] for event in db.events))[i]:
                                [event for event in db.events if list(set(event.location[event.location.find("(") + 1:-1] for event in db.events))[i] in event.location]}
                                for i in range(len(list(set(event.location[event.location.find("(") + 1:-1] for event in db.events))))]
                    }
                    for db in different_buildings
                ],
                "long_breaks": [
                    {
                        "day": lb.day,
                        "week_parity": lb.week_parity,
                        "break_time": lb.breaktime,
                        "event1": lb.events[0].to_dict(),
                        "event2": lb.events[1].to_dict()
                    }
                    for lb in long_breaks
                ],
                "short_breaks_different_campus": [
                    {
                        "day": sb.day,
                        "week_parity": sb.week_parity,
                        "break_time": sb.breaktime,
                        "event1": sb.events[0].to_dict(),
                        "event2": sb.events[1].to_dict(),
                        "different_campuses": [sb.events[0].location[0], sb.events[1].location[0]]
                    }
                    for sb in short_breaks
                ]
            })

        return response

    # Отправляем запрос на API и сохраняем результаты в базу данных
    response = await get_schedule(query)

    # Сохраняем историю запроса
    history = add_history(db, query)

    # Сохраняем группы и связываем их с историей
    for data in response:
        calname = list(data.keys())[0]
        group = add_group(db, calname)
        history_group = HistoryHasGroup(history_id=history.id, group_id=group.id)
        db.add(history_group)
        db.commit()

        # Сохраняем события
        for event in data[calname]['events_by_calname']:
            add_event(db, event, group.id)

        # Сохраняем длинные перерывы
        for long_break in data[calname]['long_breaks']:
            add_long_break(db, long_break, group.id)

        # Сохраняем короткие перерывы
        for short_break in data[calname]['short_breaks_different_campus']:
            add_short_break(db, short_break, group.id)

        # Сохраняем разные здания
        for different_building in data[calname]['different_buildings']:
            add_different_building(db, different_building, group.id)

    return response


@app.get("/different-buildings_2")
async def different_buildings_endpoint(query: str = None, db: Session = Depends(get_db)):
    # Проверяем, был ли выполнен такой запрос ранее
    history = get_history_by_text(db, query)
    if history:
        # Возвращаем данные из базы данных
        group_has_histories = db.query(HistoryHasGroup).filter(HistoryHasGroup.history_id == history.id).all()
        response = []
        for ghh in group_has_histories:
            group = db.query(Group).filter(Group.id == ghh.group_id).first()
            different_buildings = get_different_buildings_by_group_id(db, group.id)
            for different_building in different_buildings:
                different_building.events = get_events_db_by_different_building_id(db, different_building.id)
            response.append({
                group.name: {
                    "different_buildings": [
                        {
                            "day": db.day,
                            "week_parity": db.week_parity,
                            "buildings": list(
                                set(event.location[event.location.find("(") + 1:-1] for event in db.events)),
                            "events_by_building": [{list(
                                set(event.location[event.location.find("(") + 1:-1] for event in db.events))[i]:
                                    [event for event in db.events if
                                     list(set(event.location[event.location.find("(") + 1:-1]
                                            for event in db.events))[i] in event.location]}
                                            for i in range(len(list(set(event.location[event.location.find("(") + 1:-1]
                                            for event in db.events))))]
                        }
                        for db in different_buildings
                    ]
                }
            })
        return response

    # Отправляем запрос на API и сохраняем результаты в базу данных
    response = await get_schedule(query)

    # Сохраняем историю запроса
    history = add_history(db, query)

    # Сохраняем группы и связываем их с историей
    for data in response:
        calname = list(data.keys())[0]
        group = add_group(db, calname)
        history_group = HistoryHasGroup(history_id=history.id, group_id=group.id)
        db.add(history_group)
        db.commit()

        # Сохраняем события
        for event in data[calname]['events_by_calname']:
            add_event(db, event, group.id)

        # Сохраняем длинные перерывы
        for long_break in data[calname]['long_breaks']:
            add_long_break(db, long_break, group.id)

        # Сохраняем короткие перерывы
        for short_break in data[calname]['short_breaks_different_campus']:
            add_short_break(db, short_break, group.id)

        # Сохраняем разные здания
        for different_building in data[calname]['different_buildings']:
            add_different_building(db, different_building, group.id)

    return await get_different_buildings(query)


@app.get("/long-breaks_2")
async def long_breaks_endpoint(query: str = None, db: Session = Depends(get_db)):
    # Проверяем, был ли выполнен такой запрос ранее
    history = get_history_by_text(db, query)
    if history:
        # Возвращаем данные из базы данных
        group_has_histories = db.query(HistoryHasGroup).filter(HistoryHasGroup.history_id == history.id).all()
        response = []
        for ghh in group_has_histories:
            group = db.query(Group).filter(Group.id == ghh.group_id).first()
            long_breaks = get_long_breaks_by_group_id(db, group.id)
            for long_break in long_breaks:
                long_break.events = get_events_lb_by_long_break_id(db, long_break.id)
            response.append({
                group.name: {
                    "long_breaks": [
                        {
                            "day": lb.day,
                            "week_parity": lb.week_parity,
                            "break_time": lb.breaktime,
                            "event1": lb.events[0].to_dict(),
                            "event2": lb.events[1].to_dict()
                        }
                        for lb in long_breaks
                    ]
                }
            })
        return response

    # Отправляем запрос на API и сохраняем результаты в базу данных
    response = await get_schedule(query)

    # Сохраняем историю запроса
    history = add_history(db, query)

    # Сохраняем группы и связываем их с историей
    for data in response:
        calname = list(data.keys())[0]
        group = add_group(db, calname)
        history_group = HistoryHasGroup(history_id=history.id, group_id=group.id)
        db.add(history_group)
        db.commit()

        # Сохраняем события
        for event in data[calname]['events_by_calname']:
            add_event(db, event, group.id)

        # Сохраняем длинные перерывы
        for long_break in data[calname]['long_breaks']:
            add_long_break(db, long_break, group.id)

        # Сохраняем короткие перерывы
        for short_break in data[calname]['short_breaks_different_campus']:
            add_short_break(db, short_break, group.id)

        # Сохраняем разные здания
        for different_building in data[calname]['different_buildings']:
            add_different_building(db, different_building, group.id)

    return await get_long_breaks(query)


@app.get("/short-breaks-different-campus_2")
async def short_breaks_different_campus_endpoint(query: str = None, db: Session = Depends(get_db)):
    # Проверяем, был ли выполнен такой запрос ранее
    history = get_history_by_text(db, query)
    if history:
        # Возвращаем данные из базы данных
        group_has_histories = db.query(HistoryHasGroup).filter(HistoryHasGroup.history_id == history.id).all()
        response = []
        for ghh in group_has_histories:
            group = db.query(Group).filter(Group.id == ghh.group_id).first()
            short_breaks = get_short_breaks_by_group_id(db, group.id)
            for short_break in short_breaks:
                short_break.events = get_events_sb_by_short_break_id(db, short_break.id)
            response.append({
                group.name: {
                    "short_breaks_different_campus": [
                        {
                            "day": sb.day,
                            "week_parity": sb.week_parity,
                            "break_time": sb.breaktime,
                            "event1": sb.events[0].to_dict(),
                            "event2": sb.events[1].to_dict(),
                            "different_campuses": [sb.events[0].location[0], sb.events[1].location[0]]
                        }
                        for sb in short_breaks
                    ]
                }
            })
        return response

    # Отправляем запрос на API и сохраняем результаты в базу данных
    response = await get_schedule(query)

    # Сохраняем историю запроса
    history = add_history(db, query)

    # Сохраняем группы и связываем их с историей
    for data in response:
        calname = list(data.keys())[0]
        group = add_group(db, calname)
        history_group = HistoryHasGroup(history_id=history.id, group_id=group.id)
        db.add(history_group)
        db.commit()

        # Сохраняем события
        for event in data[calname]['events_by_calname']:
            add_event(db, event, group.id)

        # Сохраняем длинные перерывы
        for long_break in data[calname]['long_breaks']:
            add_long_break(db, long_break, group.id)

        # Сохраняем короткие перерывы
        for short_break in data[calname]['short_breaks_different_campus']:
            add_short_break(db, short_break, group.id)

        # Сохраняем разные здания
        for different_building in data[calname]['different_buildings']:
            add_different_building(db, different_building, group.id)

    return await get_short_breaks_different_campus(query)


async def process_request(query: str, request_id: int, request_type: str):
    """Фоновая обработка запроса."""
    try:
        # Определяем, какую функцию вызвать
        if request_type == "schedule":
            result = await get_schedule(query)
        elif request_type == "different-buildings":
            result = await get_different_buildings(query)
        elif request_type == "long-breaks":
            result = await get_long_breaks(query)
        elif request_type == "short-breaks-different-campus":
            result = await get_short_breaks_different_campus(query)
        else:
            raise ValueError(f"Unknown request type: {request_type}")

        # Функция для сериализации объектов в JSON
        def to_dict(obj):
            if isinstance(obj, list):
                return [to_dict(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: to_dict(value) for key, value in obj.items()}
            elif hasattr(obj, 'to_dict'):  # Если есть метод to_dict()
                return obj.to_dict()
            elif hasattr(obj, '__dict__'):  # SQLAlchemy-объект
                return {key: to_dict(value) for key, value in obj.__dict__.items() if not key.startswith('_')}
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return obj

        # Сериализуем результат
        result_dict = to_dict(result)

        # Открываем новую сессию БД
        with next(get_db()) as db:
            request_status = db.query(RequestStatus).filter(RequestStatus.id == request_id).first()
            if request_status:
                request_status.status = "completed"
                request_status.result = json.dumps(result_dict)  # Сохраняем результат как JSON-строку
                db.commit()
            else:
                print(f"Request {request_id} not found.")
    except Exception as e:
        print(f"Error processing request {request_id}: {e}")
        with next(get_db()) as db:
            request_status = db.query(RequestStatus).filter(RequestStatus.id == request_id).first()
            if request_status:
                request_status.status = "failed"
                request_status.result = json.dumps({"error": str(e)})
                db.commit()


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
