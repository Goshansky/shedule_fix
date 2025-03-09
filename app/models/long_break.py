from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey


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
