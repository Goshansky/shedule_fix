from fastapi import FastAPI, HTTPException
import httpx
from icalendar import Calendar
from io import BytesIO
from datetime import datetime, timedelta
import pytz
import re

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


# Функция для извлечения корпуса из "location" (в скобках)
def extract_building(location):
    match = re.search(r'\((.*?)\)', location)
    return match.group(1) if match else None


# Функция для извлечения кампуса (первая буква перед "-")
def extract_campus(location):
    match = re.match(r'([А-ЯA-Z])-', location)
    return match.group(1) if match else None


# Поиск разных корпусов в один день
def find_different_buildings(events):
    issues = []
    events_by_day = {}

    for event in events:
        key = (event["day_of_week"], event["week_parity"])
        if key not in events_by_day:
            events_by_day[key] = set()
        building = extract_building(event["location"])
        if building:
            events_by_day[key].add(building)

    for key, buildings in events_by_day.items():
        if len(buildings) > 1:
            issues.append({
                "day": key[0],
                "week_parity": key[1],
                "buildings": list(buildings)
            })

    return issues


# Поиск длинных перерывов (> 30 минут)
def find_long_breaks(events):
    issues = []
    events_by_day = {}

    for event in events:
        key = (event["day_of_week"], event["week_parity"])
        if key not in events_by_day:
            events_by_day[key] = []
        events_by_day[key].append(event)

    for key, day_events in events_by_day.items():
        day_events.sort(key=lambda e: e["start"])
        for i in range(len(day_events) - 1):
            end_time = datetime.strptime(day_events[i]["end"], "%H:%M")
            start_time = datetime.strptime(day_events[i + 1]["start"], "%H:%M")
            if start_time - end_time > timedelta(minutes=30):
                issues.append({
                    "day": key[0],
                    "week_parity": key[1],
                    "event1": day_events[i],
                    "event2": day_events[i + 1],
                    "break_time": (start_time - end_time).seconds // 60
                })

    return issues


# Поиск короткой перемены (< 30 минут) с разными кампусами
def find_short_breaks_different_campus(events):
    issues = []
    events_by_day = {}

    for event in events:
        key = (event["day_of_week"], event["week_parity"])
        if key not in events_by_day:
            events_by_day[key] = []
        events_by_day[key].append(event)

    for key, day_events in events_by_day.items():
        day_events.sort(key=lambda e: e["start"])
        for i in range(len(day_events) - 1):
            end_time = datetime.strptime(day_events[i]["end"], "%H:%M")
            start_time = datetime.strptime(day_events[i + 1]["start"], "%H:%M")
            if start_time - end_time < timedelta(minutes=30):
                campus1 = extract_campus(day_events[i]["location"])
                campus2 = extract_campus(day_events[i + 1]["location"])
                if campus1 and campus2 and campus1 != campus2:
                    issues.append({
                        "day": key[0],
                        "week_parity": key[1],
                        "event1": day_events[i],
                        "event2": day_events[i + 1],
                        "break_time": (start_time - end_time).seconds // 60,
                        "different_campuses": (campus1, campus2)
                    })

    return issues


@app.get("/schedule")
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

    different_buildings = find_different_buildings(events)
    long_breaks = find_long_breaks(events)
    short_breaks_different_campus = find_short_breaks_different_campus(events)

    return {
        "calname": calname,
        "events": events,
        "different_buildings": different_buildings,
        "long_breaks": long_breaks,
        "short_breaks_different_campus": short_breaks_different_campus
    }

