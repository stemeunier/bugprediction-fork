from datetime import datetime

def date_iso_8601_to_datetime(date_str: str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')

def datetime_to_date_hours_minuts(date_datetime: datetime):
    return date_datetime.strftime("%Y-%m-%d %H:%M")

def date_hour_to_datetime(date_str: str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')