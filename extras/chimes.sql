CREATE TABLE chime (
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
    is_active BOOLEAN,
    description CHAR(100) NOT NULL,
    filename CHAR(100) NOT NULL
);

INSERT INTO chime VALUES(NULL, 0, '17.25 Inch Master C Chakra Tibetan Singing Bowl', '01.mp3');
INSERT INTO chime VALUES(NULL, 0, '14 Inch Hand Hammered Tibetan Singing Bowl', '02.mp3');
INSERT INTO chime VALUES(NULL, 1, '11.5 Inch Large Rare Antique Singing Bowl - 18th Century', '03.mp3');
INSERT INTO chime VALUES(NULL, 0, '9.5 Inch Master Meditation Series Zen Singing Bowl', '04.mp3');
