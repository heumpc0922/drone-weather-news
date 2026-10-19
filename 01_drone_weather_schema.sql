CREATE TABLE IF NOT EXISTS drone_weather_news.station (
    station_id INT PRIMARY KEY,
    station_name VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL
);
CREATE TABLE IF NOT EXISTS drone_weather_news.observation (
    observation_id INT AUTO_INCREMENT PRIMARY KEY,
    station_id INT NOT NULL,
    observed_at DATETIME NOT NULL,
    temperature_c DECIMAL(5,1),
    precipitation_mm DECIMAL(7,1),
    wind_speed_ms DECIMAL(5,1),
    wind_direction_deg SMALLINT,
    humidity_pct TINYINT UNSIGNED,
    source VARCHAR(100) NOT NULL DEFAULT 'KMA ASOS',

    UNIQUE KEY uq_station_time (station_id, observed_at),

    CONSTRAINT fk_observation_station
        FOREIGN KEY (station_id)
        REFERENCES drone_weather_news.station(station_id),

    CONSTRAINT chk_humidity
        CHECK (humidity_pct BETWEEN 0 AND 100),

    CONSTRAINT chk_precipitation
        CHECK (precipitation_mm >= 0),

    CONSTRAINT chk_wind_speed
        CHECK (wind_speed_ms >= 0)
);

CREATE TABLE IF NOT EXISTS drone_weather_news.article (
    article_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    body TEXT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    prompt TEXT,
    status VARCHAR(10) NOT NULL DEFAULT '검토대기',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_article_status
        CHECK (status IN ('검토대기', '승인', '보류'))
);

CREATE TABLE IF NOT EXISTS drone_weather_news.article_source (
    article_id INT NOT NULL,
    observation_id INT NOT NULL,

    PRIMARY KEY (article_id, observation_id),

    CONSTRAINT fk_article_source_article
        FOREIGN KEY (article_id)
        REFERENCES drone_weather_news.article(article_id),

    CONSTRAINT fk_article_source_observation
        FOREIGN KEY (observation_id)
        REFERENCES drone_weather_news.observation(observation_id)
);

CREATE TABLE IF NOT EXISTS drone_weather_news.review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT NOT NULL,
    reviewer VARCHAR(50) NOT NULL,
    check_passed BOOLEAN NOT NULL,
    comment TEXT,
    reviewed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_review_article
        FOREIGN KEY (article_id)
        REFERENCES drone_weather_news.article(article_id)
);