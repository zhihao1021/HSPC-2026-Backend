CREATE TABLE IF NOT EXISTS users (
    uid BIGINT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    city TEXT,
    lunch TEXT,
    real_name TEXT,
    school TEXT,
    is_nanbao BOOLEAN NOT NULL DEFAULT FALSE,
    is_graduate BOOLEAN NOT NULL DEFAULT FALSE,
    team_id BIGINT,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    student_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verify_info TEXT NOT NULL DEFAULT '',
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (team_id) REFERENCES teams(uid) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_users_team_id ON users(team_id);
