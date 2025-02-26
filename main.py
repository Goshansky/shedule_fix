from fastapi import FastAPI, HTTPException
import httpx
from icalendar import Calendar
from io import BytesIO
from datetime import datetime
import pytz

app = FastAPI()

# Словарь для перевода номеров дней недели в русские названия
DAYS_OF_WEEK = {
    0: "Понедельник", 1: "Вторник", 2: "Среда",
    3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"
}


# Функция для форматирования времени
def format_time(dt):
    return dt.strftime("%H:%M")


# Функция для определения четности недели
def get_week_parity(dt):
    if 10 <= dt.day <= 16 and dt.month == 2:
        return "нечетная"
    elif 17 <= dt.day <= 23 and dt.month == 2:
        return "четная"
    return "неизвестно"


@app.get("/hello")
async def get_schedule(query: str = None):
    search_url = "https://schedule-of.mirea.ru/schedule/api/search"
    params = {"match": query} if query else {}

    async with httpx.AsyncClient() as client:
        search_response = await client.get(search_url, params=params)
        search_data = search_response.json()

    if not search_data.get("data"):
        raise HTTPException(status_code=404, detail="Расписание не найдено")

    ical_link = search_data["data"][0].get("iCalLink")
    if not ical_link:
        raise HTTPException(status_code=404, detail="iCal ссылка не найдена")

    async with httpx.AsyncClient() as client:
        ical_response = await client.get(ical_link)

    # Парсим iCal
    calendar = Calendar.from_ical(BytesIO(ical_response.content).read())

    # Получаем название календаря
    calname = calendar.get("X-WR-CALNAME")
    if calname:
        calname = str(calname)

    events = []
    for component in calendar.walk():
        if component.name == "VEVENT":
            start_dt = component.get("DTSTART").dt
            end_dt = component.get("DTEND").dt

            if isinstance(start_dt, datetime) and isinstance(end_dt, datetime):
                # Приводим к московскому времени
                start_dt = start_dt.astimezone(pytz.timezone("Europe/Moscow"))
                end_dt = end_dt.astimezone(pytz.timezone("Europe/Moscow"))

                event = {
                    "summary": str(component.get("SUMMARY")),
                    "start": format_time(start_dt),
                    "end": format_time(end_dt),
                    "day_of_week": DAYS_OF_WEEK[start_dt.weekday()],
                    "description": str(component.get("DESCRIPTION")),
                    "location": str(component.get("LOCATION")),
                    "week_parity": get_week_parity(start_dt)
                }
                events.append(event)

    return {"calname": calname, "events": events}

