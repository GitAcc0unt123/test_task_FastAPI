from src import create_fastAPI_app
from src.utils.config import Config


config = Config('config.yaml')
app = create_fastAPI_app(config.fastAPI)
