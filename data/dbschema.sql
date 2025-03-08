-- Databse schema, use on new instance creation

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Users (
    -- id and role are not necessary to insert everytime
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    fullname TEXT NOT NULL,
    qualification TEXT,
    dob DATE NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user')) NOT NULL DEFAULT 'user' 
);


CREATE TABLE IF NOT EXISTS Subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT
);


CREATE TABLE IF NOT EXISTS Chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    chap_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (subject_id) REFERENCES Subjects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Quiz (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    duration TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (chapter_id) REFERENCES Chapters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    qstatement TEXT NOT NULL,
    opt1 TEXT NOT NULL,
    opt2 TEXT NOT NULL,
    opt3 TEXT,
    opt4 TEXT,
    copt INTEGER NOT NULL, 
    FOREIGN KEY (quiz_id) REFERENCES Quiz(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    time_stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    report TEXT NOT NULL,
    marks INTEGER NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES Quiz(id) ON DELETE CASCADE
);

