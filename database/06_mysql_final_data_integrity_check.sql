
-- 최종 기상자료 보존 및 CRUD 삭제 확인

SELECT
    COUNT(*) AS total_records,
    SUM(station_id = 108) AS seoul_records,
    SUM(station_id = 9999 AND source = 'CRUD_API_TEST')
        AS remaining_demo_records
FROM drone_weather_news.observation;
