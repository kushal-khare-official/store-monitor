from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

load_dotenv()

engine = create_engine(os.environ["DB_URL"], pool_pre_ping=True)

connection = engine.connect()
