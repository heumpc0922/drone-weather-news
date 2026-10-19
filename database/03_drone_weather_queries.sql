SELECT COUNT(*) AS total_records
FROM drone_weather_news.observation;

SELECT
    COUNT(*) AS total_records,
    MIN(observed_at) AS first_time,
    MAX(observed_at) AS last_time,
    ROUND(AVG(wind_speed_ms), 2) AS avg_wind_ms,
    MAX(wind_speed_ms) AS max_wind_ms,
    SUM(CASE WHEN wind_speed_ms > 5 THEN 1 ELSE 0 END) AS over_5ms,
    SUM(CASE WHEN precipitation_mm IS NULL THEN 1 ELSE 0 END) AS rain_null_count
FROM drone_weather_news.observation
WHERE station_id = 108;

INSERT INTO drone_weather_news.station
    (station_id, station_name, region)
VALUES
    (9999, 'CRUD연습용', '가상지역');
    
    INSERT INTO drone_weather_news.observation
    (station_id, observed_at, temperature_c, precipitation_mm,
     wind_speed_ms, wind_direction_deg, humidity_pct, source)
VALUES
    (9999, '2026-10-19 12:00:00', 20.0, NULL,
     3.0, 90, 60, 'CRUD_TEST');
     
     SELECT
    observation_id,
    station_id,
    observed_at,
    temperature_c,
    wind_speed_ms,
    source
FROM drone_weather_news.observation
WHERE station_id = 9999
  AND source = 'CRUD_TEST';
  
  UPDATE drone_weather_news.observation
SET wind_speed_ms = 4.5
WHERE observation_id = 169
  AND station_id = 9999
  AND source = 'CRUD_TEST';
  
  SELECT
    observation_id,
    station_id,
    wind_speed_ms,
    source
FROM drone_weather_news.observation
WHERE observation_id = 169
  AND station_id = 9999
  AND source = 'CRUD_TEST';
  
  DELETE FROM drone_weather_news.observation
WHERE observation_id = 169
  AND station_id = 9999
  AND source = 'CRUD_TEST';
  
  SELECT
    SUM(CASE WHEN station_id = 108 THEN 1 ELSE 0 END) AS seoul_records,
    SUM(CASE WHEN station_id = 9999
              AND source = 'CRUD_TEST' THEN 1 ELSE 0 END) AS test_records,
    COUNT(*) AS total_records
FROM drone_weather_news.observation;

INSERT INTO drone_weather_news.observation
    (station_id, observed_at, temperature_c,
     precipitation_mm, wind_speed_ms,
     wind_direction_deg, humidity_pct, source)
VALUES
    (9999, '2026-10-19 13:00:00', 20.0,
     NULL, 3.0, 90, 150, 'CRUD_TEST');
     
     SELECT
    COUNT(*) AS total_records,
    SUM(CASE WHEN station_id = 108 THEN 1 ELSE 0 END) AS seoul_records,
    SUM(CASE WHEN station_id = 9999 THEN 1 ELSE 0 END) AS test_records,
    SUM(CASE WHEN humidity_pct > 100 THEN 1 ELSE 0 END) AS invalid_humidity
FROM drone_weather_news.observation;