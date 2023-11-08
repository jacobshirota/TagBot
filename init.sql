CREATE TABLE users (
    UserID INT NOT NULL,
    Mention VARCHAR(38),
    Playing ENUM('True', 'False'),
    It ENUM('True', 'False'),
    CONSTRAINT users_pk PRIMARY KEY (UserID)
);

CREATE TABLE game_logs (
    Timestamp INT NOT NULL,
    GameID INT,
    Event ENUM('START', 'END', 'PAUSE', 'RESUME', 'TAG'),
    UserID INT,
    CONSTRAINT game_logs_pk PRIMARY KEY (Timestamp),
    CONSTRAINT users_logs_fk FOREIGN KEY (UserID) REFERENCES users (UserID)
);

CREATE TABLE leaderboard (
    UserID INT NOT NULL,
    TotalTime INT,
    CONSTRAINT leaderboard_pk PRIMARY KEY (UserID),
    CONSTRAINT user_leaderboard_fk FOREIGN KEY (UserID) REFERENCES users (UserID)
);