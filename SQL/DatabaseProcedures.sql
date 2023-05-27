USE MUNIX;

DROP PROCEDURE IF EXISTS getArtistSongs;
delimiter $$
CREATE PROCEDURE getArtistSongs(artistID INT)
BEGIN
SELECT * from Songs WHERE artistID = ArtistID;
END ;$$
delimiter ;

DROP FUNCTION IF EXISTS songExists;
delimiter $$
CREATE FUNCTION songExists(sID INT) RETURNS BOOL DETERMINISTIC
BEGIN
DECLARE sExists BOOL;
SELECT count(SongID) INTO @sExists from Songs WHERE SongID = sID;
RETURN @sExists;
END ;$$
delimiter ;

DROP FUNCTION IF EXISTS playlistExists;
delimiter $$
CREATE FUNCTION playlistExists(plID INT, uID INT) RETURNS BOOL DETERMINISTIC
BEGIN
DECLARE plExists INT DEFAULT 0;
SET @plExists = 0;
SELECT PlaylistID INTO @plExists from Playlists WHERE PlaylistID = plID AND uID = UserID;
RETURN @plExists;
END ;$$
delimiter ;

DROP FUNCTION IF EXISTS playlistExistsName;
delimiter $$
CREATE FUNCTION playlistExistsName(plName varchar(64), uID INT) RETURNS INT DETERMINISTIC
BEGIN
DECLARE plExists INT DEFAULT 0;
SET @plExists = 0;
SELECT PlaylistID INTO @plExists from Playlists WHERE PlaylistName = plName AND uID = UserID;
RETURN @plExists;
END ;$$
delimiter ;

DROP PROCEDURE IF EXISTS addSongToPlaylist;
delimiter $$
CREATE PROCEDURE addSongToPlaylist(sID INT, pID INT, uID INT)
BEGIN
DECLARE success BOOL;
SET @success = songExists(sID) AND playlistExists(pID, uID);
IF @success THEN
	INSERT INTO PlaylistHasSongs VALUES (pID, sID); 
END IF;
SELECT @success;
END ;$$
delimiter ;

DROP PROCEDURE IF EXISTS createSong;
delimiter $$
CREATE PROCEDURE createSong(sName varchar(128), sPath varchar(128), sDuration INT, artistID INT, albumID INT)
BEGIN
INSERT INTO Songs (SongName, SongPath, Duration, ArtistID, AlbumID) VALUES (
	sName, sPath, sDuration, artistID, albumID
);
END ;$$
delimiter ;


DROP PROCEDURE IF EXISTS createPlaylist;
delimiter $$
CREATE PROCEDURE createPlaylist(plName varchar(64), uID INT)
BEGIN
DECLARE nameFree BOOL;
SELECT NOT count(UserID) INTO @nameFree from Playlists WHERE uID = UserID AND plName = PlaylistName;
IF @nameFree THEN
	INSERT INTO Playlists (PlaylistName, UserID) VALUES (
		plName, uID
	);
END IF;
SELECT @nameFree;
END ;$$
delimiter ;


DROP PROCEDURE IF EXISTS showPlaylistID;
delimiter $$
CREATE PROCEDURE showPlaylistID(plID INT, uID INT)
BEGIN
DECLARE allowed BOOL;
SELECT count(PlaylistID) <> 0 INTO @allowed from Playlists WHERE PlaylistID = plID AND UserID = uID;
iF @allowed THEN
	
	SELECT s.SongID, s.SongName, al.AlbumName, ar.ArtistName, s.Duration from (SELECT s.* from PlaylistHasSongs phs
			LEFT JOIN Playlists pl ON pl.PlaylistID = phs.PlaylistID
			LEFT JOIN Songs s ON s.SongID = phs.SongID
			WHERE pl.PlaylistID = plID) s
	LEFT JOIN Albums al ON al.AlbumID = s.AlbumID 
	LEFT JOIN Artists ar ON ar.ArtistID = s.ArtistID;
END IF;
END ;$$
delimiter ;

DROP PROCEDURE IF EXISTS showPlaylistName;
delimiter $$
CREATE PROCEDURE showPlaylistName(plName varchar(64), uID INT)
BEGIN 
DECLARE plID INT DEFAULT 0;
SELECT PlaylistID INTO @plID from Playlists WHERE PlaylistName = plName AND UserID = uID;
IF plID THEN
	CALL showPlaylistID(@plID, uID);
END IF;
END$$
delimiter ;


DROP PROCEDURE IF EXISTS getSongInfo;
delimiter $$
CREATE PROCEDURE getSongInfo(sName varchar(128))
BEGIN 
SELECT s.SongID, s.SongName, al.AlbumName, ar.ArtistName, s.Duration from Songs s 
INNER JOIN Albums al ON s.AlbumID = al.AlbumID 
INNER JOIN Artists ar ON s.ArtistID = ar.ArtistID
WHERE sName = s.SongName;
END$$
delimiter ;

DROP PROCEDURE IF EXISTS getSongInfoID;
delimiter $$
CREATE PROCEDURE getSongInfoID(sID INT)
BEGIN 
SELECT s.SongID, s.SongName, al.AlbumName, ar.ArtistName, s.Duration from Songs s 
INNER JOIN Albums al ON s.AlbumID = al.AlbumID 
INNER JOIN Artists ar ON s.ArtistID = ar.ArtistID
WHERE sID = s.SongID;
END$$
delimiter ;

DROP PROCEDURE IF EXISTS getSongPlaylistInfo;
delimiter $$
CREATE PROCEDURE getSongPlaylistInfo(sName varchar(64), pID INT, uID INT)
BEGIN 

SELECT s.SongID, s.SongName, al.AlbumName, ar.ArtistName, s.Duration from (SELECT s.* from Playlists p 
INNER JOIN PlaylistHasSongs phs ON p.PlaylistID = phs.PlaylistID
INNER JOIN Songs s ON phs.SongID = s.SongID
WHERE s.SongName = sName AND p.PlaylistID = pID AND p.UserID = uID) s
LEFT JOIN Albums al ON s.AlbumID = al.AlbumID
LEFT JOIN Artists ar ON s.ArtistID = ar.ArtistID;

END$$
delimiter ;

DROP PROCEDURE IF EXISTS getAllSongs;
delimiter $$
CREATE PROCEDURE getAllSongs()
BEGIN
SELECT s.SongID, s.SongName, al.AlbumName, ar.ArtistName, s.Duration from Songs s 
INNER JOIN Albums al ON s.AlbumID = al.AlbumID 
INNER JOIN Artists ar ON s.ArtistID = ar.ArtistID;
END$$
delimiter ; 

DROP PROCEDURE IF EXISTS getArtistAndAlbum;
delimiter $$
CREATE PROCEDURE getArtistAndAlbum(aName varchar(128))
BEGIN
SELECT ar.ArtistID, ar.ArtistName, al.AlbumName, al.AlbumID from Artists ar INNER JOIN Albums al ON ar.ArtistID = al.ArtistID WHERE ar.ArtistName = aName;
END$$
delimiter ;

DROP PROCEDURE IF EXISTS getAlbumID;
delimiter $$
CREATE PROCEDURE getAlbumID(aID INT)
BEGIN
SELECT a.AlbumID, a.AlbumName, s.SongID, s.SongName, ar.ArtistName, s.Duration from Songs s
INNER JOIN Albums a ON s.AlbumID = a.AlbumID
INNER JOIN Artists ar ON ar.ArtistID = a.ArtistID WHERE aID = s.AlbumID; 
END$$
delimiter ;

DROP PROCEDURE IF EXISTS getAlbumName;
delimiter $$
CREATE PROCEDURE getAlbumName(aName varchar(128))
BEGIN
SELECT al.AlbumID, al.AlbumName, ar.ArtistName from Albums al INNER JOIN Artists ar ON al.ArtistID = ar.ArtistID WHERE al.AlbumName = aName;
END$$
delimiter ;
