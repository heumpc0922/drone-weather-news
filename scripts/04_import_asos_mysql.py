"""서울 ASOS 시간별 관측자료 CSV를 MySQL에 중복 없이 저장하는 실습 코드."""
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

FOLDER = Path(__file__).resolve().parent.parent
CSV_FILE = FOLDER / "data" / "raw" / "OBS_ASOS_TIM_20261019111228.csv"
load_dotenv(FOLDER / ".env")


def optional_decimal(value):
    """빈칸은 0이 아닌 None(MySQL NULL)으로 처리합니다."""
    value = value.strip()
    return None if not value else float(value)


def optional_int(value):
    value = value.strip()
    return None if not value else int(value)


def read_and_validate():
    with CSV_FILE.open(encoding="cp949", newline="") as file:
        reader = csv.DictReader(file)
        expected_columns = {"지점", "지점명", "일시", "기온(°C)", "강수량(mm)", "풍속(m/s)", "풍향(16방위)", "습도(%)"}
        if not expected_columns.issubset(reader.fieldnames or []):
            raise ValueError("CSV 열 이름이 예상과 다릅니다.")
        result = []
        for row in reader:
            station_id = int(row["지점"])
            if station_id != 108 or row["지점명"].strip() != "서울":
                raise ValueError("서울(108) 이외의 관측소가 포함되어 있습니다.")
            dt = datetime.strptime(row["일시"], "%Y-%m-%d %H:%M")
            temperature = optional_decimal(row["기온(°C)"])
            rain = optional_decimal(row["강수량(mm)"])
            wind = optional_decimal(row["풍속(m/s)"])
            direction = optional_int(row["풍향(16방위)"])
            humidity = optional_int(row["습도(%)"])
            if rain is not None and rain < 0 or wind is not None and wind < 0:
                raise ValueError(f"잘못된 음수 관측값: {dt}")
            if humidity is not None and not 0 <= humidity <= 100:
                raise ValueError(f"습도 범위 오류: {dt}")
            result.append((station_id, dt, temperature, rain, wind, direction, humidity))
    times = sorted(x[1] for x in result)
    start = datetime(2026, 10, 12, 0)
    expected = [start + timedelta(hours=h) for h in range(168)]
    if times != expected:
        raise ValueError("시간 기록이 168개 연속인지 확인해 주세요. 중복 또는 누락이 있습니다.")
    return result


def main():
    rows = read_and_validate()  # DB를 변경하기 전에 CSV 검증
    config = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
    }
    if not all([config["user"], config["password"], config["database"]]):
        raise ValueError(".env의 MySQL 접속 설정을 확인하세요.")

    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM station WHERE station_id = %s", (108,))
        if cursor.fetchone()[0] != 1:
            raise ValueError("먼저 station 테이블에 서울(108)을 등록하세요.")
        cursor.execute("SELECT COUNT(*) FROM observation WHERE station_id = %s", (108,))
        before = cursor.fetchone()[0]
        # 같은 관측소+시간은 UNIQUE 제약으로 중복 저장되지 않습니다.
        # 같은 CSV를 다시 실행해도 이미 저장된 행은 변경하지 않습니다.
        sql = """
        INSERT INTO observation
          (station_id, observed_at, temperature_c, precipitation_mm,
           wind_speed_ms, wind_direction_deg, humidity_pct)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE observation_id = observation_id
        """
        cursor.executemany(sql, rows)
        connection.commit()
        cursor.execute("SELECT COUNT(*) FROM observation WHERE station_id = %s", (108,))
        after = cursor.fetchone()[0]
        print("=== 서울 ASOS → MySQL 저장 결과 ===")
        print("CSV 확인:", len(rows), "건")
        print("저장 전 서울 관측자료:", before, "건")
        print("새로 추가된 관측자료:", after - before, "건")
        print("저장 후 서울 관측자료:", after, "건")
        print("강수량 빈칸은 0이 아닌 MySQL NULL로 저장했습니다.")
        print("중복된 관측 시각은 추가 저장하지 않습니다.")
    except mysql.connector.Error as error:
        if connection and connection.is_connected():
            connection.rollback()
        print("MySQL 오류 번호:", error.errno)
        print("자료 저장 실패. 오류 번호를 알려주세요. 비밀번호는 공유하지 마세요.")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
