CREATE DATABASE audioExtraction;
USE audioExtraction;

CREATE TABLE fingerprints(
hashkey     varchar(20) PRIMARY KEY,
song_name   varchar(100) NOT NULL,
time_offset  int unsigned NOT NULL,
INDEX(hashkey)
);

CREATE TABLE songs(
song_id       int unsigned NOT NULL AUTO_INCREMENT UNIQUE PRIMARY KEY,
song_name     varchar(100) NOT NULL,
fingerprinted boolean DEFAULT FALSE
);
