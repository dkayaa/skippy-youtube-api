CREATE TABLE videos (
    pk INT AUTO_INCREMENT PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- api/v1
CREATE TABLE labels (
    pk INT AUTO_INCREMENT PRIMARY KEY,
    start_time FLOAT NOT NULL,
    label INT NOT NULL,
    video_fk INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_fk) REFERENCES videos(pk)
);

-- api/v2
CREATE TABLE intervals (
    pk INT AUTO_INCREMENT PRIMARY KEY,
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    orgs VARCHAR(1000) DEFAULT '',
    video_fk INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_fk) REFERENCES videos(pk)
)