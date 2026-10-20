
-- CRUD 통합 테스트
-- 기존 168건은 유지하고 테스트용 데이터만 사용합니다.

USE drone_weather_news;

START TRANSACTION;

-- C: 테스트용 관측자료 등록
INSERT INTO observation
    (station_id, observed_at, temperature_c,
     precipitation_mm, wind_speed_ms,
     wind_direction_deg, humidity_pct, source)
VALUES
    (9999, '2026-10-20 12:00:00', 20.0,
     0.0, 3.0, 90, 60, 'CRUD_TEST');

-- R: 등록된 데이터 조회
SELECT observation_id, station_id, observed_at,
       wind_speed_ms, source
FROM observation
WHERE station_id = 9999
  AND source = 'CRUD_TEST';

-- U: 풍속을 3.0에서 4.5로 수정
UPDATE observation
SET wind_speed_ms = 4.5
WHERE station_id = 9999
  AND observed_at = '2026-10-20 12:00:00'
  AND source = 'CRUD_TEST';

-- R: 수정된 풍속 확인
SELECT observation_id, wind_speed_ms
FROM observation
WHERE station_id = 9999
  AND source = 'CRUD_TEST';

-- D: 테스트 데이터 삭제
DELETE FROM observation
WHERE station_id = 9999
  AND observed_at = '2026-10-20 12:00:00'
  AND source = 'CRUD_TEST';

-- R: 테스트 데이터가 삭제됐는지 확인
SELECT COUNT(*) AS remaining_test_records
FROM observation
WHERE station_id = 9999
  AND source = 'CRUD_TEST';

-- 연습 중 발생한 변경사항 취소
ROLLBACK;

-- 최종 데이터 건수 확인
SELECT COUNT(*) AS final_observation_count
FROM observation;
