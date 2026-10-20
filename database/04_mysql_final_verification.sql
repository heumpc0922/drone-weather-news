
-- 드론 기상정보 프로젝트 MySQL 최종 조회 점검

USE drone_weather_news;

-- 1. 전체 기상 관측 건수
SELECT COUNT(*) AS total_observations
FROM observation;

-- 2. 서울 ASOS 관측 건수
SELECT COUNT(*) AS seoul_observations
FROM observation
WHERE station_id = 108;

-- 3. 최근 관측자료 5건
SELECT observed_at, temperature_c,
       wind_speed_ms, humidity_pct
FROM observation
WHERE station_id = 108
ORDER BY observed_at DESC
LIMIT 5;

-- 4. MySQL의 테이블 목록
SHOW TABLES;
