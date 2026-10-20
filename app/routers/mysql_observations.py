"""SQL CRUD 학습용 API: ASOS 실측 108번은 절대 변경하지 않습니다."""
import os
from datetime import datetime
from decimal import Decimal
from typing import Annotated

import mysql.connector
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.database import db_session

router = APIRouter(prefix="/api/mysql", tags=["MySQL CRUD (교육용)"])
DEMO_STATION_ID = 9999
DEMO_SOURCE = "CRUD_API_TEST"

class ObservationCreate(BaseModel):
    observed_at: datetime
    temperature_c: float | None = Field(default=None, ge=-100, le=100)
    precipitation_mm: float | None = Field(default=None, ge=0)
    wind_speed_ms: float = Field(ge=0, le=200)
    wind_direction_deg: int | None = Field(default=None, ge=0, le=360)
    humidity_pct: int | None = Field(default=None, ge=0, le=100)

class ObservationUpdate(BaseModel):
    wind_speed_ms: float = Field(ge=0, le=200)

def allow_write():
    if os.getenv("ENABLE_DEMO_CRUD", "false").lower() != "true":
        raise HTTPException(403, "쓰기 기능이 꺼져 있습니다. 로컬 .env에 ENABLE_DEMO_CRUD=true로 설정하세요.")

def db_failure(exc):
    raise HTTPException(503, "MySQL에 접속하거나 쿼리를 실행할 수 없습니다.") from exc

def serialize(row):
    for k, v in row.items():
        if isinstance(v, (datetime,)):
            row[k] = v.isoformat(sep=" ")
        elif isinstance(v, Decimal):
            row[k] = float(v)
    return row

@router.get("/observations")
def list_observations(limit: Annotated[int, Query(ge=1, le=168)] = 20):
    """서울 108번은 읽기 전용, 최신 관측자료."""
    try:
        with db_session() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT observation_id, station_id, observed_at, temperature_c, "
                    "precipitation_mm, wind_speed_ms, wind_direction_deg, humidity_pct, source "
                    "FROM observation WHERE station_id = %s ORDER BY observed_at DESC LIMIT %s",
                    (108, limit))
                return {"station_id": 108, "rows": [serialize(r) for r in cur.fetchall()]}
            finally:
                cur.close()
    except mysql.connector.Error as exc:
        db_failure(exc)

@router.get("/demo")
def list_demo():
    """현재 임시 실습자료 조회 (서울 원본과 분리됨)."""
    try:
        with db_session() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT observation_id, station_id, observed_at, wind_speed_ms, source "
                    "FROM observation WHERE station_id=%s AND source=%s ORDER BY observation_id DESC LIMIT 50",
                    (DEMO_STATION_ID, DEMO_SOURCE))
                return {"rows": [serialize(r) for r in cur.fetchall()]}
            finally:
                cur.close()
    except mysql.connector.Error as exc:
        db_failure(exc)

@router.post("/demo", status_code=201)
def create_demo(item: ObservationCreate):
    allow_write()
    try:
        with db_session() as conn:
            cur = conn.cursor()
            try:
                # 실습관측소 9999번이 존재하는 DB에서만 동작합니다.
                cur.execute(
                    "INSERT INTO observation "
                    "(station_id, observed_at, temperature_c, precipitation_mm, wind_speed_ms, "
                    "wind_direction_deg, humidity_pct, source) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (DEMO_STATION_ID, item.observed_at, item.temperature_c, item.precipitation_mm,
                     item.wind_speed_ms, item.wind_direction_deg, item.humidity_pct, DEMO_SOURCE))
                record_id = cur.lastrowid
                conn.commit()
                return {"observation_id": record_id, "message": "실습자료 등록 완료"}
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()
    except mysql.connector.IntegrityError as exc:
        raise HTTPException(409, "같은 시각의 자료가 있거나 실습관측소 9999가 없습니다.") from exc
    except mysql.connector.Error as exc:
        db_failure(exc)

@router.patch("/demo/{observation_id}")
def update_demo(observation_id: int, item: ObservationUpdate):
    allow_write()
    try:
        with db_session() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "UPDATE observation SET wind_speed_ms=%s "
                    "WHERE observation_id=%s AND station_id=%s AND source=%s",
                    (item.wind_speed_ms, observation_id, DEMO_STATION_ID, DEMO_SOURCE))
                updated = cur.rowcount
                conn.commit()
                if not updated:
                    raise HTTPException(404, "수정 가능한 실습자료가 아닙니다.")
                return {"observation_id": observation_id, "message": "실습자료 수정 완료"}
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()
    except mysql.connector.Error as exc:
        db_failure(exc)

@router.delete("/demo/{observation_id}")
def delete_demo(observation_id: int):
    allow_write()
    try:
        with db_session() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "DELETE FROM observation WHERE observation_id=%s AND station_id=%s AND source=%s",
                    (observation_id, DEMO_STATION_ID, DEMO_SOURCE))
                deleted = cur.rowcount
                conn.commit()
                if not deleted:
                    raise HTTPException(404, "삭제 가능한 실습자료가 아닙니다.")
                return {"observation_id": observation_id, "message": "실습자료 삭제 완료"}
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()
    except mysql.connector.Error as exc:
        db_failure(exc)
