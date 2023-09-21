import enum
from sqlalchemy import Boolean, BigInteger, Column, DateTime, Enum, MetaData, Table
from config.db import engine

metadata_obj = MetaData()


class ActiveEnum(enum.Enum):
    inactive = 0
    active = 1


poll_table = Table(
    "poll",
    metadata_obj,
    Column("id", BigInteger, primary_key=True),
    Column("store_id", BigInteger),
    Column("timestamp_utc", DateTime),
    Column("status", Enum(ActiveEnum, name="activeenum"), default=ActiveEnum.active),
)

metadata_obj.create_all(engine)
