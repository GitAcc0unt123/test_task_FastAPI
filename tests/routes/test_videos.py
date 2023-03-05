from typing import TYPE_CHECKING

from src.utils.config import Config

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_route_videos(client: 'TestClient'):
    """Функция для тестирования получаемого от сервера списка файлов в папке с видео.

    Args:
        client: Тестовый клиент.
    """
    config = Config()
    video_dir_path = config.fastAPI['VIDEOS_DIR_PATH']
    expected = [
        {
            "file_name": "sample-1.mp4",
            "file_path": f"{video_dir_path}/sample-1.mp4"
        },
        {
            "file_name": "sample-2.mp4",
            "file_path": f"{video_dir_path}/sample-2.mp4"
        },
        {
            "file_name": "sample-3.mp4",
            "file_path": f"{video_dir_path}/sample-3.mp4"
        },
        {
            "file_name": "пример-1.mp4",
            "file_path": f"{video_dir_path}/пример-1.mp4"
        },
        {
            "file_name": "corrupted_file.mp4",
            "file_path": f"{video_dir_path}/corrupted_file.mp4"
        },
        {
            "file_name": "sample 0.mp4",
            "file_path": f"{video_dir_path}/sample 0.mp4"
        },
    ]

    response = client.get('/api/videos')
    assert response.status_code == 200
    assert sorted(response.json(), key=lambda x: x['file_name']) == sorted(expected, key=lambda x: x['file_name'])

    # check idempotent
    response = client.get('/api/videos')
    assert response.status_code == 200
    assert sorted(response.json(), key=lambda x: x['file_name']) == sorted(expected, key=lambda x: x['file_name'])
