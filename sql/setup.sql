#CREATE DATABASE audioExtraction;
#USE audioExtraction;
DROP tables fingerprints, songs;

CREATE TABLE fingerprints(
hashkey     varchar(20) PRIMARY KEY,
song_name   varchar(100) NOT NULL,
time_offset  int unsigned NOT NULL,
INDEX(hashkey)
);

CREATE TABLE songs(
song_id       int unsigned AUTO_INCREMENT PRIMARY KEY,
song_name     varchar(100) NOT NULL,
fgp           binary DEFAULT 0
);
