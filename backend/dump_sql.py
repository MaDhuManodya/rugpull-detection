import os
import sys

from sqlalchemy import create_mock_engine
from sqlalchemy.schema import CreateTable

# Add backend to path so we can import app
sys.path.insert(0, os.path.abspath("."))

from app.database.base import Base
from app.models import *

def dump(sql, *multiparams, **params):
    print(sql.compile(dialect=engine.dialect))

engine = create_mock_engine('postgresql+psycopg2://', dump)

print("--- SQL DUMP ---")
Base.metadata.create_all(engine, checkfirst=False)
