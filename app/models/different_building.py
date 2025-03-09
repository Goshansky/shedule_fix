from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey


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
