from app.database import add_history, add_group, HistoryHasGroup, add_event, add_long_break, add_short_break, \
    add_different_building, SessionLocal, Group, get_history_by_text, get_events_by_group_id, get_long_breaks_by_group_id, \
    get_short_breaks_by_group_id, get_different_buildings_by_group_id, get_events_lb_by_long_break_id, \
    get_events_sb_by_short_break_id, get_events_db_by_different_building_id, get_group_by_name
from app.services.schedule_service import get_schedule, get_different_buildings, get_long_breaks, get_short_breaks_different_campus
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/schedule")
async def schedule_endpoint(query: str = None, db: Session = Depends(get_db)):
    # Проверяем, был ли выполнен такой запрос ранее
    history = get_history_by_text(db, query)
    if history:
        print("1")
        # Возвращаем данные из базы данных
        group = db.query(Group).filter(Group.id == history.id).first()
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

        return {
            "events_by_calname": {group.name: [event.to_dict() for event in events]},
            "different_buildings": [
                {
                    "day": db.day,
                    "week_parity": db.week_parity,
                    "buildings": list(set(event.location[event.location.find("(")+1:-1] for event in db.events)),
                    "events_by_building": [{list(set(event.location[event.location.find("(")+1:-1] for event in db.events))[i]: [event for event in db.events if list(set(event.location[event.location.find("(")+1:-1] for event in db.events))[i] in event.location]}
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
        }

    # Проверяем наличие группы в таблице groups
    group = get_group_by_name(db, query)
    if group:
        print("2")
        # Возвращаем данные из базы данных
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

        return {
            "events_by_calname": {group.name: [event.to_dict() for event in events]},
            "different_buildings": [
                {
                    "day": db.day,
                    "week_parity": db.week_parity,
                    "buildings": list(set(event.location[event.location.find("(")+1:-1] for event in db.events)),
                    "events_by_building": {building: [event.to_dict() for event in events] for building, events in db.events_by_building.items()}
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
        }
    print("222")
    # Отправляем запрос на API и сохраняем результаты в базу данных
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
