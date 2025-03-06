from app.models.event import Event
from app.services.schedule_service import find_different_buildings, find_long_breaks, find_short_breaks_different_campus
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
