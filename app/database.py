from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import Session

from app.services.schedule_service import get_schedule
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:password@localhost:5431/schedule"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class RequestStatus(Base):
    __tablename__ = "request_status"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String, index=True)
    status = Column(String, default="in_progress")  # in_progress, completed
    result = Column(JSON, nullable=True)  # если запрос завершен, сюда можно сохранить результат

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


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    def to_dict(self):
        return {
            "name": self.name
        }

class History(Base):
    __tablename__ = 'histories'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)

    def to_dict(self):
        return {
            "text": self.text
        }

class HistoryHasGroup(Base):
    __tablename__ = 'history_has_groups'
    history_id = Column(Integer, ForeignKey('histories.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String, index=True)
    start_time = Column(String, index=True)
    end_time = Column(String, index=True)
    day_of_week = Column(String, index=True)
    description = Column(String, index=True)
    location = Column(String, index=True)
    week_parity = Column(String, index=True)
    groups_id = Column(Integer, ForeignKey('groups.id'))

    def to_dict(self):
        return {
            "summary": self.summary,
            "start": self.start_time,
            "end": self.end_time,
            "day_of_week": self.day_of_week,
            "description": self.description,
            "location": self.location,
            "week_parity": self.week_parity
        }

class LongBreak(Base):
    __tablename__ = 'long_breaks'
    id = Column(Integer, primary_key=True, index=True)
    day = Column(String, index=True)
    week_parity = Column(String, index=True)
    breaktime = Column(Integer, index=True)
    groups_id = Column(Integer, ForeignKey('groups.id'))

    def to_dict(self):
        return {
            "day": self.day,
            "week_parity": self.week_parity,
            "break_time": self.breaktime
        }

class ShortBreak(Base):
    __tablename__ = 'short_breaks'
    id = Column(Integer, primary_key=True, index=True)
    day = Column(String, index=True)
    week_parity = Column(String, index=True)
    breaktime = Column(Integer, index=True)
    groups_id = Column(Integer, ForeignKey('groups.id'))

    def to_dict(self):
        return {
            "day": self.day,
            "week_parity": self.week_parity,
            "break_time": self.breaktime
        }

class DifferentBuilding(Base):
    __tablename__ = 'different_buildings'
    id = Column(Integer, primary_key=True, index=True)
    day = Column(String, index=True)
    week_parity = Column(String, index=True)
    groups_id = Column(Integer, ForeignKey('groups.id'))

    def to_dict(self):
        return {
            "day": self.day,
            "week_parity": self.week_parity
        }

class EventDB(Base):
    __tablename__ = 'events_db'
    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String, index=True)
    start_time = Column(String, index=True)
    end_time = Column(String, index=True)
    day_of_week = Column(String, index=True)
    description = Column(String, index=True)
    location = Column(String, index=True)
    week_parity = Column(String, index=True)
    different_buildings_id = Column(Integer, ForeignKey('different_buildings.id'))
    different_buildings_groups_id = Column(Integer, ForeignKey('groups.id'))

    def to_dict(self):
        return {
            "summary": self.summary,
            "start": self.start_time,
            "end": self.end_time,
            "day_of_week": self.day_of_week,
            "description": self.description,
            "location": self.location,
            "week_parity": self.week_parity
        }

class EventLB(Base):
    __tablename__ = 'events_lb'
    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String, index=True)
    start_time = Column(String, index=True)
    end_time = Column(String, index=True)
    day_of_week = Column(String, index=True)
    description = Column(String, index=True)
    location = Column(String, index=True)
    week_parity = Column(String, index=True)
    long_breaks_id = Column(Integer, ForeignKey('long_breaks.id'))
    long_breaks_groups_id = Column(Integer, ForeignKey('groups.id'))

    def to_dict(self):
        return {
            "summary": self.summary,
            "start": self.start_time,
            "end": self.end_time,
            "day_of_week": self.day_of_week,
            "description": self.description,
            "location": self.location,
            "week_parity": self.week_parity
        }

class EventSB(Base):
    __tablename__ = 'events_sb'
    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String, index=True)
    start_time = Column(String, index=True)
    end_time = Column(String, index=True)
    day_of_week = Column(String, index=True)
    description = Column(String, index=True)
    location = Column(String, index=True)
    week_parity = Column(String, index=True)
    short_breaks_id = Column(Integer, ForeignKey('short_breaks.id'))
    short_breaks_groups_id = Column(Integer, ForeignKey('groups.id'))

    def to_dict(self):
        return {
            "summary": self.summary,
            "start": self.start_time,
            "end": self.end_time,
            "day_of_week": self.day_of_week,
            "description": self.description,
            "location": self.location,
            "week_parity": self.week_parity
        }


Base.metadata.create_all(bind=engine)


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
