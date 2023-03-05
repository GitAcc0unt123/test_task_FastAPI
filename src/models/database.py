from sqlalchemy import create_engine

from src.utils.config import Config
from .tables.frame_service_information import metadata

DATABASE_URL = Config().fastAPI['SQLALCHEMY_DATABASE_URI']

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)
