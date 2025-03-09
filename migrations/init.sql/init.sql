CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE histories (
    id SERIAL PRIMARY KEY,
    text VARCHAR(255)
);

CREATE TABLE history_has_groups (
    history_id INT REFERENCES histories(id) ON DELETE CASCADE,
    group_id INT REFERENCES groups(id) ON DELETE CASCADE,
    PRIMARY KEY (history_id, group_id)
);

CREATE TABLE long_breaks (
    id SERIAL PRIMARY KEY,
    day VARCHAR(255),
    week_parity VARCHAR(255),
    breaktime INT,
    groups_id INT REFERENCES groups(id) ON DELETE CASCADE
);

CREATE TABLE short_breaks (
    id SERIAL PRIMARY KEY,
    day VARCHAR(255),
    week_parity VARCHAR(255),
    breaktime INT,
    groups_id INT REFERENCES groups(id) ON DELETE CASCADE
);

CREATE TABLE different_buildings (
    id SERIAL PRIMARY KEY,
    day VARCHAR(255),
    week_parity VARCHAR(255),
    groups_id INT REFERENCES groups(id) ON DELETE CASCADE
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    summary VARCHAR(255),
    start_time VARCHAR(255),
    end_time VARCHAR(255),
    day_of_week VARCHAR(255),
    description VARCHAR(255),
    location VARCHAR(255),
    week_parity VARCHAR(255),
    groups_id INT REFERENCES groups(id) ON DELETE CASCADE
);

CREATE TABLE events_lb (
    id SERIAL PRIMARY KEY,
    summary VARCHAR(255),
    start_time VARCHAR(255),
    end_time VARCHAR(255),
    day_of_week VARCHAR(255),
    description VARCHAR(255),
    location VARCHAR(255),
    week_parity VARCHAR(255),
    long_breaks_id INT REFERENCES long_breaks(id) ON DELETE CASCADE,
    long_breaks_groups_id INT REFERENCES groups(id) ON DELETE CASCADE
);

CREATE TABLE events_db (
    id SERIAL PRIMARY KEY,
    summary VARCHAR(255),
    start_time VARCHAR(255),
    end_time VARCHAR(255),
    day_of_week VARCHAR(255),
    description VARCHAR(255),
    location VARCHAR(255),
    week_parity VARCHAR(255),
    different_buildings_id INT REFERENCES different_buildings(id) ON DELETE CASCADE,
    different_buildings_groups_id INT REFERENCES groups(id) ON DELETE CASCADE
);

CREATE TABLE events_sb (
    id SERIAL PRIMARY KEY,
    summary VARCHAR(255),
    start_time VARCHAR(255),
    end_time VARCHAR(255),
    day_of_week VARCHAR(255),
    description VARCHAR(255),
    location VARCHAR(255),
    week_parity VARCHAR(255),
    short_breaks_id INT REFERENCES short_breaks(id) ON DELETE CASCADE,
    short_breaks_groups_id INT REFERENCES groups(id) ON DELETE CASCADE
);

CREATE TABLE request_status (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'in_progress' NOT NULL,
    result JSONB NULL
);