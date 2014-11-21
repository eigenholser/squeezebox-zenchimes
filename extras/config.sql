CREATE TABLE config (
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
    section CHAR(30) NOT NULL,
    parameter CHAR(100) NOT NULL,
    value CHAR(100) NOT NULL,
    description CHAR(100) NOT NULL
);

INSERT INTO config VALUES(NULL, 'zenchimes', 'debug', 'False', 'Debug mode is for development or troubleshooting.');
INSERT INTO config VALUES(NULL, 'zenchimes', 'loglevel', 'DEBUG', 'Logging verbosity.');
INSERT INTO config VALUES(NULL, 'zenchimes', 'chime_enabled', 'True', 'Global setting that enables or disables playing of chimes.');
INSERT INTO config VALUES(NULL, 'server', 'http_listen_ip_addr', '0.0.0.0', 'IP address HTTP server will bind.');
INSERT INTO config VALUES(NULL, 'server', 'http_listen_ip_port', '8000', 'IP port HTTP server will bind.');
INSERT INTO config VALUES(NULL, 'scheduler', 'timezone', 'America/Denver', 'Timezone.');
INSERT INTO config VALUES(NULL, 'scheduler', 'starttime', '07:00:00', 'Time of day chimes will become active.');
INSERT INTO config VALUES(NULL, 'scheduler', 'endtime', '22:00:00', 'Time of day chimes will become inactive.');
INSERT INTO config VALUES(NULL, 'scheduler', 'chime_interval', '1200', 'Interval in seconds between chimes.');
INSERT INTO config VALUES(NULL, 'player', 'lms_hostname', '127.0.0.1', 'Logitech Media Server hostname.');
INSERT INTO config VALUES(NULL, 'player', 'lms_port', '9090', 'Logitech Media Server Command Line Interface Port.');
INSERT INTO config VALUES(NULL, 'player', 'mixer_volume', '50', 'Volume to set the squeezebox players for playing chimes.');
INSERT INTO config VALUES(NULL, 'player', 'lms_chime_path', '/srv/data/music/misc/Singing Bowl', 'Filesystem path of the chime audio files.');
