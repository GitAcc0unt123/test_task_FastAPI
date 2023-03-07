import os
import shutil
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert

from src import create_fastAPI_app
from src.utils.config import Config
from src.models import metadata
from src.models import frame_service_informations

if TYPE_CHECKING:
    from fastapi import FastAPI
    from sqlalchemy import Engine


@pytest.fixture(scope="session")
def app() -> 'FastAPI':
    """Функция для создания FastAPI приложения.

    Returns:
        FastAPI приложение.
    """
    config = Config('config.yaml')
    app = create_fastAPI_app(config.fastAPI)
    return app


@pytest.fixture(scope="function")
def engine() -> 'Engine':
    """Функция для очистки базы данных.

    Returns:
        Подключение к базе данных с таблицами и без данных.
    """
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URI')
    engine = create_engine(DATABASE_URL)
    metadata.drop_all(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def client(app: 'FastAPI') -> TestClient:
    """Функция для создания тестового клиента.

    Args:
        app: FastAPI приложение.

    Returns:
        Тестовый клиент.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
def clean_frames_dir() -> None:
    """Функция для удаления всех файлов и каталогов из указанного в конфигурационном файле каталога с сохранёнными фреймами.
    """
    config = Config()
    frames_dir_path = config.fastAPI['FRAMES_DIR_PATH']
    for dir_name in os.listdir(frames_dir_path):
        dir_path = os.path.join(frames_dir_path, dir_name)
        shutil.rmtree(dir_path)


def create_frame_service_information(
        engine: 'Engine',
        video_file_name: str,
        frame_number: int,
        frame_file_path: str,
) -> None:
    """Функция для добавления в базу данных строки со служебной информацией о вырезанном кадре.

    Args:
        engine: Подключение к базе данных с таблицами и без данных.
        video_file_name: Имя исходного видеофайла.
        frame_number: Порядковый номер вырезанного кадра от начала файла.
        frame_file_path: Полный путь к файлу с вырезанный кадром.
    """
    with engine.connect() as conn:
        stmt = insert(frame_service_informations).values(
            video_file_name=video_file_name,
            frame_number=frame_number,
            frame_file_path=frame_file_path
        )
        conn.execute(stmt)
        conn.commit()
