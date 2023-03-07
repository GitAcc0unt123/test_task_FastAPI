import os

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from src.utils.config import Config


videos_router = APIRouter()

@videos_router.get('')
def get_video_list() -> JSONResponse:
    """Возвращает список имён файлов и полный путь к ним из указанного в конфигурационном файле каталога с видео.
    """
    try:
        video_dir_path = Config().fastAPI['VIDEOS_DIR_PATH']
        response_data = [
            {
                "file_name": filename,
                "file_path": os.path.join(video_dir_path, filename)
            }
            for filename in os.listdir(video_dir_path)
            if os.path.isfile(os.path.join(video_dir_path, filename))
        ]
        return JSONResponse(response_data, status.HTTP_200_OK)
    except Exception:
        return JSONResponse({"data": 'Something went wrong'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
