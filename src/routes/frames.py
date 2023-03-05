import os

import cv2
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.utils.config import Config
from src.utils.get_frames import extract_frame


frames_router = APIRouter()


@frames_router.get('')
def get_frames(file_name: str, time_in_video: int):
    """Возвращает номер первого кадра и массив строк с маршрутами к файлам с кадрами.

    Params:
        file_name (str): Имя видеофайла.
        time_in_video (int): Время от начала видеофайла в секундах.
    """
    # file access by relative paths ../../../something
    simple_filename_check = lambda x: os.pathsep not in x and ".." not in x

    # field constraints
    constraint_failed = {}
    if len(file_name) == 0:
        constraint_failed['file_name'] = 'Shorter than minimum length 1.'
    elif not simple_filename_check(file_name):
        constraint_failed['file_name'] = 'Forbidden file name.'
    if time_in_video < 0:
        constraint_failed['time_in_video'] = 'Less than minimum value 0.'
    if len(constraint_failed) > 0:
        return JSONResponse(constraint_failed, 400)

    # check the existence of the file
    config = Config()
    video_path = os.path.join(config.fastAPI['VIDEOS_DIR_PATH'], file_name)
    if not os.path.isfile(video_path):
        return JSONResponse({'file_name': "File doesn't exist."}, 400)

    # extract frames
    first_frame, frames = extract_frame(video_path, time_in_video)
    if len(frames) != config.fastAPI['SAVE_FRAMES_COUNT'] or first_frame is None:
        return JSONResponse({'message': 'Failed to extract frames.'}, 500)

    # save images
    try:
        frame_dir = os.path.join(config.fastAPI['FRAMES_DIR_PATH'], file_name)
        if not os.path.exists(frame_dir):
            os.mkdir(frame_dir)
        elif os.path.isfile(frame_dir):
            return JSONResponse({'message': 'Frame directory is file'}, 500)

        frame_paths = []
        for (i, frame) in enumerate(frames):
            frame_name = f'{first_frame + i}.png'
            frame_path = os.path.join(frame_dir, frame_name)
            frame_paths.append(frame_path)
            cv2.imwrite(frame_path, frame)
    except Exception:
        return JSONResponse({'message': 'Something went wrong'}, 500)

    response_data = {
        "first_frame": first_frame,
        "file_paths": frame_paths
    }
    return JSONResponse(response_data, 200)
