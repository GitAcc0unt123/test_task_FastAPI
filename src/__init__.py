from fastapi import FastAPI

from src.routes import videos_router, frames_router, saved_frames_router


def create_fastAPI_app(config: dict) -> FastAPI:
    """Функция для создания FastAPI приложения.
    
    Args:
        config: Конфигурация FastAPI приложения.

    Returns:
        FastAPI приложение.
    """
    app = FastAPI()
    app.include_router(videos_router, prefix='/api/videos', tags=['videos'])
    app.include_router(frames_router, prefix='/api/frames', tags=['frames'])
    app.include_router(saved_frames_router, prefix='/api/saved_frames', tags=['saved frames'])

    return app