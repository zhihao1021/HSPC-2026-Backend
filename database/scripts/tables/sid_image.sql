CREATE TABLE IF NOT EXISTS sid_image (
    uid BIGINT PRIMARY KEY,
    user_uid BIGINT NOT NULL,
    image_front BYTEA,
    image_back BYTEA,

    FOREIGN KEY (user_uid) REFERENCES users(uid) ON DELETE CASCADE
);