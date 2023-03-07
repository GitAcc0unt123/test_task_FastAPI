import os

from sqlalchemy import create_engine

from src.models import metadata


if __name__ == '__main__':
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URI')
    engine = create_engine(DATABASE_URL)
    metadata.drop_all(engine)
    metadata.create_all(engine)