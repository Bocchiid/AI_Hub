# src/core/config.py

from dotenv import load_dotenv
import os

# load dotenv file
load_dotenv()
# get api_key from dotenv file
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DOUBAO_API_KEY = os.getenv('DOUBAO_API_KEY')

# get model_name from dotenv file
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL')
DOUBAO_MODEL = os.getenv('DOUBAO_MODEL')
DOUBAO_IMAGE_MODEL = os.getenv('DOUBAO_IMAGE_MODEL')

# get mongodb_url and database_name from dotenv file
MONGODB_URL = os.getenv('MONGODB_URL')
DATABASE_NAME = os.getenv('DATABASE_NAME')

# get jwt relative configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))