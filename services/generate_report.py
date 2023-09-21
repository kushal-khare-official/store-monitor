import datetime
from sqlalchemy import select

from config.db import engine
from models.index import (
    business_hour_table,
    poll_table,
    report_table,
    timezone_table,
    ActiveEnum,
    StatusEnum,
)
from utils.csv import save_report
from utils.time import (
    local_datetime_to_utc,
    local_time_to_utc,
    time_difference_in_minutes,
)


DEFAULT_TIMEZONE = "America/Chicago"

CURRENT_TIME = datetime.datetime.fromisoformat("2023-01-25T18:13:22.479220")
LAST_WEEK = CURRENT_TIME - datetime.timedelta(days=7)
LAST_DAY = CURRENT_TIME - datetime.timedelta(days=1)
LAST_HOUR = CURRENT_TIME - datetime.timedelta(hours=1)

DEFAULT_BUSINESS_HOURS = {
    "start_time": datetime.time(0, 0),
    "end_time": datetime.time(23, 59),
}

DEFAULT_REPORT = {
    "uptime_last_hour": 0,
    "downtime_last_hour": 0,
    "uptime_last_day": 0,
    "downtime_last_day": 0,
    "uptime_last_week": 0,
    "downtime_last_week": 0,
}

connection = engine.connect()


def generate_report(file_name):
    timezones = fetch_timezones()

    local_business_hours = fetch_local_business_hours()
    utc_business_hours = local_business_hours_to_utc(local_business_hours, timezones)

    poll_data = fetch_poll_data()

    report_data = calculate_report_data(poll_data, utc_business_hours)
    formatted_report_data = format_report_data(report_data)

    save_report(file_name, formatted_report_data)

    update_report_status(file_name)


def fetch_timezones():
    query = select(timezone_table.c.store_id, timezone_table.c.timezone_str)

    timezone_data = connection.execute(query).mappings().all()

    timezones = {}

    for timezone in timezone_data:
        timezones[timezone["store_id"]] = timezone["timezone_str"]

    return timezones


def fetch_local_business_hours():
    query = business_hour_table.select()

    return connection.execute(query).mappings().all()


def local_business_hours_to_utc(local_business_hours, timezones):
    utc_business_hours = {}

    for business_hour in local_business_hours:
        store_id = business_hour["store_id"]
        weekday = business_hour["day_of_week"]
        timezone_str = timezones.get(store_id, DEFAULT_TIMEZONE)

        utc_business_hour = {
            "start_time": local_time_to_utc(
                business_hour["start_time_local"], timezone_str
            ),
            "end_time": local_time_to_utc(
                business_hour["end_time_local"], timezone_str
            ),
        }

        if utc_business_hours.get(store_id, None) == None:
            utc_business_hours[store_id] = {}

        utc_business_hours[store_id][weekday] = utc_business_hour

    return utc_business_hours


def fetch_poll_data():
    query = (
        select(poll_table.c.store_id, poll_table.c.timestamp_utc, poll_table.c.status)
        .where(poll_table.c.timestamp_utc > LAST_WEEK)
        .order_by(poll_table.c.timestamp_utc.desc())
    )

    return connection.execute(query).mappings().all()


def poll_in_business_hours(poll_data, business_hours):
    day_of_week = poll_data["timestamp_utc"].weekday()
    business_hour = business_hours.get(day_of_week, DEFAULT_BUSINESS_HOURS.copy())

    return (
        business_hour["start_time"]
        <= poll_data.timestamp_utc.time()
        <= business_hour["end_time"]
    )


def calculate_report_data(poll_data, business_hours):
    report_data = {}
    last_poll_data = {}

    for current_poll in poll_data:
        if not poll_in_business_hours(current_poll, business_hours):
            continue

        store_id = current_poll["store_id"]

        report = report_data.get(store_id, DEFAULT_REPORT.copy())
        last_poll = last_poll_data.get(
            store_id,
            {
                "store_id": store_id,
                "timestamp_utc": CURRENT_TIME,
                "status": current_poll["status"],
            },
        )

        duration = time_difference_in_minutes(
            last_poll["timestamp_utc"], current_poll["timestamp_utc"]
        )

        if current_poll["status"] != last_poll["status"]:
            report["uptime_last_week"] += duration / 2
            report["downtime_last_week"] += duration / 2
        elif current_poll["status"] == ActiveEnum.active:
            report["uptime_last_week"] += duration
        else:
            report["downtime_last_week"] += duration

        if current_poll["timestamp_utc"] > LAST_HOUR:
            report["uptime_last_hour"] = report["uptime_last_week"]
            report["downtime_last_hour"] = report["downtime_last_week"]

        if current_poll["timestamp_utc"] > LAST_DAY:
            report["uptime_last_day"] = report["uptime_last_week"]
            report["downtime_last_day"] = report["downtime_last_week"]

        report_data[store_id] = report
        last_poll_data[store_id] = current_poll

    return report_data


def format_report_data(report_data):
    formatted_data = []

    for store_id in report_data:
        row = [store_id] + [value for value in report_data[store_id].values()]
        formatted_data.append(row)

    return formatted_data


def update_report_status(file_name):
    query = (
        report_table.update()
        .values(status=StatusEnum.complete)
        .where(report_table.c.file_name == file_name)
    )

    response = connection.execute(query)
    connection.commit()
