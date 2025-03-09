from app.database import Base
from sqlalchemy import Column, Integer, String


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    def to_dict(self):
        return {
            "name": self.name
        }
