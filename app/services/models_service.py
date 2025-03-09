
from app.models.event_DB import EventDB
from app.models.event_SB import EventSB
from app.models.event_LB import EventLB
from app.models.event import Event

from app.models.history import History

from app.models.group import Group
from app.models.long_break import LongBreak
from app.models.short_break import ShortBreak
from app.models.different_building import DifferentBuilding


def get_history_by_text(db, text):
    return db.query(History).filter(History.text == text).first()


def get_group_by_name(db, name):
    return db.query(Group).filter(Group.name == name).first()


def get_events_by_group_id(db, group_id):
    return db.query(Event).filter(Event.groups_id == group_id).all()


def get_long_breaks_by_group_id(db, group_id):
    return db.query(LongBreak).filter(LongBreak.groups_id == group_id).all()


def get_short_breaks_by_group_id(db, group_id):
    return db.query(ShortBreak).filter(ShortBreak.groups_id == group_id).all()


def get_different_buildings_by_group_id(db, group_id):
    return db.query(DifferentBuilding).filter(DifferentBuilding.groups_id == group_id).all()


def get_events_db_by_different_building_id(db, different_building_id):
    return db.query(EventDB).filter(EventDB.different_buildings_id == different_building_id).all()


def get_events_lb_by_long_break_id(db, long_break_id):
    return db.query(EventLB).filter(EventLB.long_breaks_id == long_break_id).all()


def get_events_sb_by_short_break_id(db, short_break_id):
    return db.query(EventSB).filter(EventSB.short_breaks_id == short_break_id).all()


def add_history(db, text):
    history = History(text=text)
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def add_group(db, name):
    group = Group(name=name)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def add_event(db, event, group_id):
    event_db = Event(
        summary=event.summary,
        start_time=event.start,
        end_time=event.end,
        day_of_week=event.day_of_week,
        description=event.description,
        location=event.location,
        week_parity=event.week_parity,
        groups_id=group_id
    )
    db.add(event_db)
    db.commit()
    db.refresh(event_db)
    return event_db


def add_long_break(db, long_break, group_id):
    long_break_db = LongBreak(
        day=long_break['day'],
        week_parity=long_break['week_parity'],
        breaktime=long_break['break_time'],
        groups_id=group_id
    )
    db.add(long_break_db)
    db.commit()
    db.refresh(long_break_db)

    # Добавляем события для длинных перерывов
    for event in [long_break['event1'], long_break['event2']]:
        event_lb = EventLB(
            summary=event.summary,
            start_time=event.start,
            end_time=event.end,
            day_of_week=event.day_of_week,
            description=event.description,
            location=event.location,
            week_parity=event.week_parity,
            long_breaks_id=long_break_db.id,
            long_breaks_groups_id=group_id
        )
        db.add(event_lb)
        db.commit()
        db.refresh(event_lb)

    return long_break_db


def add_short_break(db, short_break, group_id):
    short_break_db = ShortBreak(
        day=short_break['day'],
        week_parity=short_break['week_parity'],
        breaktime=short_break['break_time'],
        groups_id=group_id
    )
    db.add(short_break_db)
    db.commit()
    db.refresh(short_break_db)

    # Добавляем события для коротких перерывов
    for event in [short_break['event1'], short_break['event2']]:
        event_sb = EventSB(
            summary=event.summary,
            start_time=event.start,
            end_time=event.end,
            day_of_week=event.day_of_week,
            description=event.description,
            location=event.location,
            week_parity=event.week_parity,
            short_breaks_id=short_break_db.id,
            short_breaks_groups_id=group_id
        )
        db.add(event_sb)
        db.commit()
        db.refresh(event_sb)

    return short_break_db


def add_different_building(db, different_building, group_id):
    different_building_db = DifferentBuilding(
        day=different_building['day'],
        week_parity=different_building['week_parity'],
        groups_id=group_id
    )
    db.add(different_building_db)
    db.commit()
    db.refresh(different_building_db)

    # Добавляем события для разных зданий
    for building, events in different_building['events_by_building'].items():
        for event in events:
            event_db = EventDB(
                summary=event.summary,
                start_time=event.start,
                end_time=event.end,
                day_of_week=event.day_of_week,
                description=event.description,
                location=event.location,
                week_parity=event.week_parity,
                different_buildings_id=different_building_db.id,
                different_buildings_groups_id=group_id
            )
            db.add(event_db)
            db.commit()
            db.refresh(event_db)

    return different_building_db
