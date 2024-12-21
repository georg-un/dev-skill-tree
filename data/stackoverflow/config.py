import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_CONFIG = {
    "dbname": os.getenv('POSTGRES_DBNAME'),
    "user": os.getenv('POSTGRES_USER'),
    "password": os.getenv('POSTGRES_PASSWORD'),
    "host": os.getenv('POSTGRES_HOST'),
    "port": os.getenv('POSTGRES_PORT'),
}
