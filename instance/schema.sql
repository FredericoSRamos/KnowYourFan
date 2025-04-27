DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    birthdate DATE NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    about TEXT NOT NULL,
    events TEXT,
    purchases TEXT,
    password TEXT NOT NULL
);