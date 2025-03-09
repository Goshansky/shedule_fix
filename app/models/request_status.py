from app.database import Base
from sqlalchemy import Column, Integer, String, JSON


class RequestStatus(Base):
    __tablename__ = "request_status"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String, index=True)
    status = Column(String, default="in_progress")  # in_progress, completed
    result = Column(JSON, nullable=True)  # если запрос завершен, сюда можно сохранить результат
