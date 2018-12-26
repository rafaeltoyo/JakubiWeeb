
SELECT count(*)
FROM anime;

SELECT *
FROM anime
LIMIT 42,45;

SELECT *
FROM anime
WHERE anime.id = 43;

SELECT *
FROM anime
INNER JOIN music
    ON anime.id = music.fk_music_anime_id;

SELECT *
FROM anime
WHERE editdist3(anime.title, "Mdka mga");

SELECT *
FROM anime
WHERE anime.title LIKE 'Dragon%';

DROP TABLE music;
DROP TABLE anime;

commit;
rollback;

CREATE VIRTUAL TABLE anime_music
USING FTS5(anime, ref, music, artirts, folder, tokenize = "porter ascii");

DROP TABLE anime_music;

SELECT * FROM anime_music;

SELECT *
FROM anime_music
WHERE anime_music = "\"k on!\""
ORDER BY rank;

SELECT * FROM anime_music
WHERE folder LIKE (
    SELECT music.filename as ref FROM music WHERE music.id = 53
)
ORDER BY rank;

SELECT anime_music.*, music.id
    FROM anime_music
INNER JOIN music
    ON anime_music.folder LIKE music.filename
WHERE anime_music MATCH "madoka"
ORDER BY rank
LIMIT 20;
