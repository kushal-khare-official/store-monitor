from sqlalchemy import BigInteger, Column, MetaData, String, Table
from config.db import engine

metadata_obj = MetaData()

timezone_table = Table(
    "timezone",
    metadata_obj,
    Column("id", BigInteger, primary_key=True),
    Column("store_id", BigInteger),
    Column("timezone_str", String),
)

metadata_obj.create_all(engine)
