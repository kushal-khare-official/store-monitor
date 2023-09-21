import enum
from sqlalchemy import (
    BigInteger,
    Column,
    Enum,
    MetaData,
    Table,
    text,
    Time,
)
from config.db import engine, connection

metadata_obj = MetaData()


class DayOfWeekEnum(enum.Enum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


business_hour_table = Table(
    "business_hour",
    metadata_obj,
    Column("id", BigInteger, primary_key=True),
    Column("store_id", BigInteger),
    Column("day_of_week", Enum(DayOfWeekEnum)),
    Column("start_time_local", Time),
    Column("end_time_local", Time),
)

metadata_obj.create_all(engine)
