import httpx
from icalendar import Calendar
from io import BytesIO
from fastapi import HTTPException
from app.services.event_service import process_events
from app.config.settings import SEARCH_URL


async def get_schedule(query: str = None):
    params = {"match": query} if query else {}

    async with httpx.AsyncClient() as client:
        search_response = await client.get(SEARCH_URL, params=params)
        search_data = search_response.json()

    if not search_data.get("data"):
        raise HTTPException(status_code=404, detail="Расписание не найдено")

    ical_link = search_data["data"][0].get("iCalLink")
    if not ical_link:
        raise HTTPException(status_code=404, detail="iCal ссылка не найдена")

    async with httpx.AsyncClient() as client:
        ical_response = await client.get(ical_link)

    calendar = Calendar.from_ical(BytesIO(ical_response.content).read())
    calname = str(calendar.get("X-WR-CALNAME")) if calendar.get("X-WR-CALNAME") else None

    events = process_events(calendar)

    return {
        "calname": calname,
        "events": events["events"],
        "different_buildings": events["different_buildings"],
        "long_breaks": events["long_breaks"],
        "short_breaks_different_campus": events["short_breaks_different_campus"]
    }
