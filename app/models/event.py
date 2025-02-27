from pydantic import BaseModel


class Event(BaseModel):
    summary: str
    start: str
    end: str
    day_of_week: str
    description: str
    location: str
    week_parity: str
