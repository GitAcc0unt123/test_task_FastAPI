import os
from typing import TYPE_CHECKING

from sqlalchemy import select

from tests.conftest import create_frame_service_information
from src.utils.config import Config
from src.models import frame_service_informations

if TYPE_CHECKING:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from sqlalchemy import Engine


def test_route_saved_frames_get_empty_list(client: 'TestClient', engine: 'Engine'):
    """Функция для тестирования получаемого от сервера списка сохранённых кадров со служебной информацией.

    Args:
        client: Тестовый клиент.
        engine: Подключение к базе данных с таблицами и без данных.
    """
    response = client.get('/api/saved_frames')
    assert response.status_code == 200
    assert response.json() == []

    # check idempotent
    response = client.get('/api/saved_frames')
    assert response.status_code == 200
    assert response.json() == []


def test_route_saved_frames_get(client: 'TestClient', app: 'FastAPI', engine: 'Engine'):
    """Функция для тестирования получаемого от сервера списка сохранённых кадров со служебной информацией.

    Args:
        client: Тестовый клиент.
        app: Flask приложение.
        engine: Подключение к базе данных с таблицами и без данных.
    """
    frame_service_information1 = {
        "video_file_name": "file_name1",
        "frame_number": 1,
        "frame_file_path": "path1",
    }
    frame_service_information2 = {
        "video_file_name": "file_name2",
        "frame_number": 3,
        "frame_file_path": "path2",
    }
    create_frame_service_information(engine, **frame_service_information1)
    create_frame_service_information(engine, **frame_service_information2)

    response = client.get('/api/saved_frames')
    assert response.status_code == 200
    assert response.json() == [ frame_service_information1, frame_service_information2 ]

    # check idempotent
    response = client.get('/api/saved_frames')
    assert response.status_code == 200
    assert response.json() == [ frame_service_information1, frame_service_information2 ]


def test_route_saved_frames_new_file_without_body(client: 'TestClient'):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с пустым телом запроса.

    Args:
        client: Тестовый клиент.
    """
    response = client.post('/api/saved_frames/new_frame')
    assert response.status_code == 422


def test_route_saved_frames_new_file_empty_json_body(client: 'TestClient'):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с отсутствующими параметрами.

    Args:
        client: Тестовый клиент.
    """
    response = client.post('/api/saved_frames/new_frame', json={})
    assert response.status_code == 422


def test_route_saved_frames_new_file_field_types(client: 'TestClient'):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с параметрами неправильного типа.

    Args:
        client: Тестовый клиент.
    """
    response = client.post('/api/saved_frames/new_frame', json={
        'file_path': None,
        'frame_number': '1'
    })
    assert response.status_code == 422


def test_route_saved_frames_new_file_constraints(client: 'TestClient'):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с недопустимыми значениями параметров.

    Args:
        client: Тестовый клиент.
    """
    response = client.post('/api/saved_frames/new_frame', json={
        'file_path': '',
        'frame_number': -1
    })
    assert response.status_code == 422


def test_route_saved_frames_new_file_file_doesnt_exist(client: 'TestClient'):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с несуществующим именем файла.

    Args:
        client: Тестовый клиент.
    """
    body = {
        'file_path': 'sampl.mp4', # имя видеофайла
        'frame_number': 1
    }
    response = client.post('/api/saved_frames/new_frame', json=body)
    assert response.status_code == 400
    assert response.json() == {
        "message": "Frame doesn't exist."
    }


def test_route_saved_frames_new_file_frame_doesnt_exist(
        client: 'TestClient',
        clean_frames_dir: None
):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с несуществующим фреймом.

    Args:
        client: Тестовый клиент.
        clean_frames_dir: Вызов фикстуры для удаления всех файлов в каталоге с фреймами перед выполнением теста.
    """
    body = {
        'file_path': 'sample-1.mp4', # имя видеофайла
        'frame_number': 10
    }
    response = client.post('/api/saved_frames/new_frame', json=body)
    assert response.status_code == 400
    assert response.json() == {
        "message": "Frame doesn't exist."
    }


def test_route_saved_frames_create(
        client: 'TestClient',
        engine: 'Engine',
        clean_frames_dir: None
):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file при сохранении служебной информации в БД.

    Args:
        client: Тестовый клиент.
        engine: Подключение к базе данных с таблицами и без данных.
        clean_frames_dir: Вызов фикстуры для удаления всех файлов в каталоге с фреймами перед выполнением теста.
    """
    # make frames
    response = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=0')
    assert response.status_code == 200

    request_body = {
        'file_path': 'sample-1.mp4', # имя видеофайла
        'frame_number': 1
    }
    response = client.post('/api/saved_frames/new_frame', json=request_body)

    frames_dir_path = Config().fastAPI['FRAMES_DIR_PATH']
    assert response.status_code == 201
    assert response.json() == {
        'file_path': 'sample-1.mp4',
        'frame_number': 1,
        "frame_path": os.path.join(frames_dir_path, 'sample-1.mp4', '1.png')
    }

    # read record from database
    with engine.connect() as conn:
        result = conn.execute(select(frame_service_informations)).all()

    assert len(result) == 1
    assert result[0].video_file_name == 'sample-1.mp4'
    assert result[0].frame_number == 1
    assert result[0].frame_file_path == os.path.join(frames_dir_path, 'sample-1.mp4', '1.png')

    # repeat request
    response = client.post('/api/saved_frames/new_frame', json=request_body)
    assert response.status_code == 400

    with engine.connect() as conn:
        result = conn.execute(select(frame_service_informations)).all()
    assert len(result) == 1
    assert result[0].video_file_name == 'sample-1.mp4'
    assert result[0].frame_number == 1
    assert result[0].frame_file_path == os.path.join(frames_dir_path, 'sample-1.mp4', '1.png')
