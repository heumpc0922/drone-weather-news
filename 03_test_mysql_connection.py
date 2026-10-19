
# MySQL 연결 테스트 프로그램
# 비밀번호를 코드에 직접 적지 않습니다.

import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

# 현재 Python 파일과 같은 폴더의 .env를 읽습니다.
env_path = Path(__file__).with_name(".env")
load_dotenv(env_path)

try:
    # .env의 설정값을 이용해 MySQL에 접속합니다.
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )

    if connection.is_connected():
        print("MySQL 연결 성공!")

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE()")
        result = cursor.fetchone()

        print("연결된 데이터베이스:", result[0])
        cursor.close()

    connection.close()

except mysql.connector.Error as error:
    print("MySQL 연결 실패")
    print("오류 번호:", error.errno)
    print("오류 종류:", type(error).__name__)
    # 비밀번호 등이 포함될 수 있으므로 오류 전문은 출력하지 않습니다.
