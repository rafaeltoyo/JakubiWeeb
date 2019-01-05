
CREATE TABLE IF NOT EXISTS anime (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    folder TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS music (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    filename TEXT NOT NULL UNIQUE,
    fk_music_anime_id INTEGER NOT NULL,
    FOREIGN KEY(fk_music_anime_id) REFERENCES anime(id)
);

CREATE VIRTUAL TABLE IF NOT EXISTS search_tool
                    USING FTS5(name, filename, artists, nickname, folder);
DROP TABLE search_tool;
