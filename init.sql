CREATE TABLE users (
    UserID INTEGER NOT NULL,
    Mention TEXT,
    Playing TEXT CHECK (Playing IN ('True', 'False')),
    It TEXT CHECK (It IN ('True', 'False')),
    CONSTRAINT users_pk PRIMARY KEY (UserID)
);

CREATE TABLE game_logs (
    Timestamp INT NOT NULL,
    GameID INTEGER,
    Event TEXT CHECK (Event IN ('START', 'END', 'PAUSE', 'RESUME', 'TAG')),
    UserID INTEGER,
    CONSTRAINT game_logs_pk PRIMARY KEY (Timestamp),
    CONSTRAINT users_logs_fk FOREIGN KEY (UserID) REFERENCES users (UserID)
);

CREATE TABLE leaderboard (
    UserID INTEGER NOT NULL,
    TotalTime INTEGER,
    CONSTRAINT leaderboard_pk PRIMARY KEY (UserID),
    CONSTRAINT user_leaderboard_fk FOREIGN KEY (UserID) REFERENCES users (UserID)
);