
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

CREATE VIRTUAL TABLE anime_music
USING FTS5(anime_name, music_title, artist);

DROP TABLE posts;

INSERT INTO anime_music(anime_name,music_title)
VALUES
    ('Madoka Magica', 'Connect', 'Claris'),
    ('Madoka Magica', 'Magia', 'Kalafina');

SELECT * FROM anime_music;

SELECT *
FROM anime_music
WHERE posts MATCH 'madoka';

SELECT *
FROM anime_music
WHERE anime_music MATCH 'claris connect'
ORDER BY rank;

rollback;


