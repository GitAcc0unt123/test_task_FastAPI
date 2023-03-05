from sqlalchemy import create_engine

from src.utils.config import Config
from src.models import metadata


if __name__ == '__main__':
    DATABASE_URL = Config().fastAPI['SQLALCHEMY_TEST_DATABASE_URI']
    engine = create_engine(DATABASE_URL)
    metadata.drop_all(engine)
    metadata.create_all(engine)