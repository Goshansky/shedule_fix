from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey


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
