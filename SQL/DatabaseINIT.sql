CREATE DATABASE MUNIX;
USE MUNIX;

CREATE TABLE Users (
	UserID INT NOT NULL AUTO_INCREMENT,
    Username varchar(64),
    primary key(UserID),
    unique(Username)
);

CREATE TABLE Playlists (
	PlaylistID INT NOT NULL AUTO_INCREMENT,
    PlaylistName varchar(64),
    UserID INT,
    primary key(PlaylistID),
    foreign key (UserID) REFERENCES Users(UserID)
);

CREATE TABLE Artists (
	ArtistID INT NOT NULL AUTO_INCREMENT,
    ArtistName varchar(128),
    primary key(ArtistID)
);

CREATE TABLE Albums (
	AlbumID INT NOT NULL AUTO_INCREMENT,
    AlbumName varchar(128),
    ArtistID INT,
    primary key (AlbumID),
    foreign key (ArtistID) REFERENCES Artists(ArtistID)
);

CREATE TABLE Songs (
	SongID INT NOT NULL AUTO_INCREMENT,
    SongName varchar(128),
    SongPath varchar(128),
    Duration INT,
    ArtistID INT,
    AlbumID INT,
    primary key (SongID),
    foreign key (ArtistID) REFERENCES Artists(ArtistID),
    foreign key (AlbumID) REFERENCES Albums(AlbumID)
);

CREATE TABLE PlaylistHasSongs (
	PlaylistID INT,
    SongID INT,
    foreign key (PlaylistID) REFERENCES Playlists(PlaylistID),
    foreign key (SongID) REFERENCES Songs(SongID)
);


