import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field

from src.models import engine
from src.models import frame_service_informations
from src.utils.config import Config


saved_frames_router = APIRouter()

@saved_frames_router.get('')
def get_saved_frames():
    """Возвращает список сохранённых кадров со служебной информацией из базы данных.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(select(frame_service_informations)).all()
        response_data = [
            {
                "video_file_name": x.video_file_name,
                "frame_number": x.frame_number,
                "frame_file_path": x.frame_file_path,
            }
            for x in result
        ]
        return JSONResponse(response_data, 200)
    except Exception as err:
        return JSONResponse({ 'message': 'Something went wrong' }, 500)


class ServiceInfoSchema(BaseModel):
    file_path: str = Field(min_length=1)
    frame_number: int = Field(gt=0)


@saved_frames_router.post('/new_frame')
def create_saved_frame(service_info: ServiceInfoSchema):
    """Сохраняет в БД служебную информацию о ранее сохранённом кадре.

    Params:
        file_path (str): Имя видеофайла
        frame_number (int): Номер кадра
    """
    video_file_name = service_info.file_path
    frame_number = service_info.frame_number

    # check frame
    config = Config()
    frame_name = f'{frame_number}.png'
    frame_path = os.path.join(config.fastAPI['FRAMES_DIR_PATH'], video_file_name, frame_name)
    if not os.path.isfile(frame_path):
        return JSONResponse({ "message": "Frame doesn't exist." }, 400)

    try:
        with engine.connect() as conn:
            stmt = insert(frame_service_informations).values(
                video_file_name=video_file_name,
                frame_number=frame_number,
                frame_file_path=frame_path
            )
            conn.execute(stmt)
            conn.commit()
        response = {
            "file_path": video_file_name,
            "frame_number": frame_number,
            "frame_path": frame_path
        }
        return JSONResponse(response, 201)
    except IntegrityError:
        return JSONResponse(None, status_code=400)
    except Exception:
        return JSONResponse(None, status_code=500)
