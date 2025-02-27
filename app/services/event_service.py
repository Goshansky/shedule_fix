from app.models.event import Event
from app.utils.date_utils import format_time, get_week_parity, DAYS_OF_WEEK
from app.utils.string_utils import extract_building, extract_campus
from datetime import datetime, timedelta
import pytz


def process_events(calendar):
    events = []
    for component in calendar.walk():
        if component.name == "VEVENT":
            start_dt = component.get("DTSTART").dt
            end_dt = component.get("DTEND").dt

            if isinstance(start_dt, datetime) and isinstance(end_dt, datetime):
                start_dt = start_dt.astimezone(pytz.timezone("Europe/Moscow"))
                end_dt = end_dt.astimezone(pytz.timezone("Europe/Moscow"))

                event = Event(
                    summary=str(component.get("SUMMARY")),
                    start=format_time(start_dt),
                    end=format_time(end_dt),
                    day_of_week=DAYS_OF_WEEK[start_dt.weekday()],  # Используем строковые названия дней недели
                    description=str(component.get("DESCRIPTION")),
                    location=str(component.get("LOCATION")),
                    week_parity=get_week_parity(start_dt)
                )
                events.append(event)

    different_buildings = find_different_buildings(events)
    long_breaks = find_long_breaks(events)
    short_breaks_different_campus = find_short_breaks_different_campus(events)

    return {
        "events": events,
        "different_buildings": different_buildings,
        "long_breaks": long_breaks,
        "short_breaks_different_campus": short_breaks_different_campus
    }


def find_different_buildings(events):
    issues = []
    events_by_day = {}

    for event in events:
        key = (event.day_of_week, event.week_parity)
        if key not in events_by_day:
            events_by_day[key] = []
        events_by_day[key].append(event)

    for key, day_events in events_by_day.items():
        buildings = set()
        events_by_building = {}
        for event in day_events:
            building = extract_building(event.location)
            if building:
                buildings.add(building)
                if building not in events_by_building:
                    events_by_building[building] = []
                events_by_building[building].append(event)

        if len(buildings) > 1:
            issues.append({
                "day": key[0],
                "week_parity": key[1],
                "buildings": list(buildings),
                "events_by_building": events_by_building
            })

    return issues


def find_long_breaks(events):
    issues = []
    events_by_day = {}

    for event in events:
        key = (event.day_of_week, event.week_parity)
        if key not in events_by_day:
            events_by_day[key] = []
        events_by_day[key].append(event)

    for key, day_events in events_by_day.items():
        day_events.sort(key=lambda e: e.start)
        for i in range(len(day_events) - 1):
            end_time = datetime.strptime(day_events[i].end, "%H:%M")
            start_time = datetime.strptime(day_events[i + 1].start, "%H:%M")
            if start_time - end_time > timedelta(minutes=30):
                issues.append({
                    "day": key[0],
                    "week_parity": key[1],
                    "event1": day_events[i],
                    "event2": day_events[i + 1],
                    "break_time": (start_time - end_time).seconds // 60
                })

    return issues


def find_short_breaks_different_campus(events):
    issues = []
    events_by_day = {}

    for event in events:
        key = (event.day_of_week, event.week_parity)
        if key not in events_by_day:
            events_by_day[key] = []
        events_by_day[key].append(event)

    for key, day_events in events_by_day.items():
        day_events.sort(key=lambda e: e.start)
        for i in range(len(day_events) - 1):
            end_time = datetime.strptime(day_events[i].end, "%H:%M")
            start_time = datetime.strptime(day_events[i + 1].start, "%H:%M")
            if start_time - end_time < timedelta(minutes=30):
                campus1 = extract_campus(day_events[i].location)
                campus2 = extract_campus(day_events[i + 1].location)
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
