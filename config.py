import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "server": os.getenv("DB_SERVER"),
    "database": os.getenv("DB_NAME"),
    "driver": os.getenv("DB_DRIVER"),
}