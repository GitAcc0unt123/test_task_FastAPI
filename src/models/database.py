import os

from sqlalchemy import create_engine

DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URI')
engine = create_engine(DATABASE_URL)