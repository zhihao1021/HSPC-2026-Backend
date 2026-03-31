CREATE TABLE IF NOT EXISTS sid_image (
    uid BIGINT PRIMARY KEY,
    user_uid BIGINT NOT NULL,
    image_front BYTEA,
    image_back BYTEA,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_uid) REFERENCES users(uid) ON DELETE CASCADE
);