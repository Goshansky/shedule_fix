from app.database import Base
from sqlalchemy import Column, Integer, String


class History(Base):
    __tablename__ = 'histories'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)

    def to_dict(self):
        return {
            "text": self.text
        }
