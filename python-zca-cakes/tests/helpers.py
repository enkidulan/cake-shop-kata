import arrow

def convert_to_date(day, base_time=None):
    part_of_a_day = 0
    if not base_time:
        base_time = arrow.get("2021.04.01")
    if "afternoon" in day:
        day = day.replace("afternoon", "").strip()
        part_of_a_day = 12
    elif "morning" in day:
        day = day.replace("morning", "").strip()
        part_of_a_day = 0
    # part_of_a_day = 12 if part_of_a_day == "afternoon" else 0
    if "next-" in day:
        day = day[5:]
        base_time = base_time.shift(days=7)
    if day not in arrow.locales.EnglishLocale.day_names:
        try:
            return arrow.get(day, "D MMMM YYYY")
        except Exception:
            return arrow.get(day)
    weekday = arrow.locales.EnglishLocale.day_names.index(day) - 1
    base_time = base_time.shift(hours=part_of_a_day)
    return base_time.shift(weekday=weekday)
