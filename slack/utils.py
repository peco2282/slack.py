from datetime import datetime


def ts2time(time: str) -> datetime:
    return datetime.fromtimestamp(float(time))
