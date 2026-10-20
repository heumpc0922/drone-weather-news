"""MySQL 접속은 요청마다 열고 닫습니다. 실제 비밀번호를 소스에 넣지 않습니다."""
import os
from pathlib import Path
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "drone_weather_news"),
        connection_timeout=5,
    )

@contextmanager
def db_session():
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()
