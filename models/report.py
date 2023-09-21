import enum
from sqlalchemy import (
    Boolean,
    BigInteger,
    Column,
    Enum,
    MetaData,
    String,
    Table,
)
from config.db import engine

metadata_obj = MetaData()


class StatusEnum(enum.Enum):
    running = 0
    complete = 1


report_table = Table(
    "report",
    metadata_obj,
    Column("id", BigInteger, primary_key=True),
    Column("status", Enum(StatusEnum), default=StatusEnum.running),
    Column("file_name", String),
)

metadata_obj.create_all(engine)
