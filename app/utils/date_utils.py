DAYS_OF_WEEK = {
    0: "Понедельник", 1: "Вторник", 2: "Среда",
    3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"
}


def format_time(dt):
    return dt.strftime("%H:%M")


def get_week_parity(dt):
    if 10 <= dt.day <= 16 and dt.month == 2:
        return "нечетная"
    elif 17 <= dt.day <= 23 and dt.month == 2:
        return "четная"
    return "неизвестно"
