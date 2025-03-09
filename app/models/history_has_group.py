from app.database import Base
from sqlalchemy import Column, Integer, ForeignKey


class HistoryHasGroup(Base):
    __tablename__ = 'history_has_groups'
    history_id = Column(Integer, ForeignKey('histories.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
