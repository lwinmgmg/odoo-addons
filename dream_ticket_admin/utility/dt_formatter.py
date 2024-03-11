from datetime import datetime, timezone

def convert_dt_str(data: dict):
    for key in data:
        if isinstance(data[key], datetime):
            data[key] = data[key].astimezone(timezone.utc).isoformat()
    return data

def remove_dt_tz(data: dict):
    for key in data:
        if isinstance(data[key], datetime):
            data[key] = data[key].astimezone(timezone.utc).replace(tzinfo=None)
    return data
