import pytz
import datetime
import time


def local_datetime_to_utc(local_datetime, timezone_str):
    timezone = pytz.timezone(timezone_str)

    return local_datetime.astimezone(pytz.utc).replace(tzinfo=None)


def local_time_to_utc(local_time, timezone_str):
    timezone = pytz.timezone(timezone_str)

    local_datetime = timezone.localize(datetime.datetime.combine(datetime.date.today(), local_time))

    return local_datetime.astimezone(pytz.utc).time()


def time_difference_in_minutes(time1, time2):
    delta = time1 - time2

    return delta.total_seconds() // 60
