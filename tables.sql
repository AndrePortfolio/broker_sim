CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL, hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 10000.00
);

CREATE TABLE portfolio (
    symbol VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (symbol, user_id)
);

CREATE TABLE history (
    symbol VARCHAR(10) NOT NULL,
    shares INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    timestamp DATETIME NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE sqlite_sequence(name,seq);

CREATE UNIQUE INDEX username ON users (username);
