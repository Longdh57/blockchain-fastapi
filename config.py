import os

from dotenv import load_dotenv

from pydantic import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Settings(BaseSettings):
    PROJECT_NAME = os.getenv('PROJECT_NAME', 'Blockchain - LOCAL')
    DEBUG = os.getenv('DEBUG', True)


settings = Settings()
