-- Databse schema, use on new instance creation

CREATE TABLE IF NOT EXISTS Users (
    -- id and role are not necessary to insert everytime
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user')) NOT NULL DEFAULT 'user' 
);

CREATE TABLE IF NOT EXISTS Subject (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS Chapter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (subject_id) REFERENCES Subject(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Quiz (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    date_of_quiz DATE NOT NULL,
    time_duration TEXT NOT NULL, -- this is HH:MM
    remarks TEXT,
    FOREIGN KEY (chapter_id) REFERENCES Chapter(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    question_statement TEXT NOT NULL,
    option1 TEXT NOT NULL,
    option2 TEXT NOT NULL,
    option3 TEXT,
    option4 TEXT,
    correct_option INTEGER NOT NULL, -- store as int 1-4
    FOREIGN KEY (quiz_id) REFERENCES Quiz(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Score (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    time_stamp_of_attempt DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_scored INTEGER NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES Quiz(id) ON DELETE CASCADE
);

