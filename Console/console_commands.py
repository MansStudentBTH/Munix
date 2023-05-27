from mysqlx import DatabaseError
import time
from Console.Player import Player

INSERT_USER = "INSERT INTO Users (Username) VALUES ('{}');"
TRANSACTION = "START TRANSACTION;"
COMMIT = "COMMIT;"
ROLLBACK = "ROLLBACK;"

ALL_COMMANDS = [
    "ls",
    "cd",
    "mkuser",
    "mkplaylist",
    "play",
    "quit",
    "song",
    "artist",
    "playing",
    "ishere",
    "add"
]
INVALID_ARGUMENT = "The argument is '{}' invalid."
NEEDS_ARGUMENT = "Command needs argument."

def print_error(msg):
    print(msg, end="\n\n")

def sqlsafe(func):
    def wrapper(session, in_str : str):
        # safe check
        forbidden = ["'", '"', "`"]
        if any(i in in_str for i in forbidden):
            return print_error(f"The input '{in_str}' is invalid.")
        func(session, in_str)
    return wrapper


def execute_sql(session, *sql_query, error_msg = ""):
    if not sql_query:
        return []
    
    result_arr = []
    session.sql(TRANSACTION).execute()
    for query_str in sql_query:
        try:
            result_arr.append(
                session.sql(query_str).execute()
            )
        except DatabaseError as de:
            session.sql(ROLLBACK).execute()
            if not error_msg:
                print_error("Database error:\n"+de.msg)
            else:
                print_error(error_msg)
            return None
        
    session.sql(COMMIT).execute()
    ret = result_arr
    if len(result_arr) == 1:
        ret = result_arr[0]

    return ret

def print_users(result):
    print("Users:")
    print("-"*60)
    for (uid, username) in result:
        print(f"{uid} | {username}")
    print("-"*60)

def show_users(state, in_str):
    result = execute_sql(state.session, 'SELECT * from Users').fetch_all()
    print_users(result)
    
def cd_prev_state(state, in_str):
    if not in_str:
        return print_error(NEEDS_ARGUMENT)
    if not in_str == "..":
        return print_error("Cannot reach that directory from here.\n")
    state.prev()

@sqlsafe
def mkuser_SelectUser(state, in_str):
    if not in_str:
        return print_error(INVALID_ARGUMENT.format(in_str))
    execute_sql(
        state.session, 
        INSERT_USER.format(in_str))

@sqlsafe
def select_user(state, in_str : str):
    result = None
    if not in_str:
        return print_error(INVALID_ARGUMENT.fromat(in_str))

    if in_str.isdigit():
        result = execute_sql(
            state.session,
            f"SELECT * from Users WHERE UserID = {in_str}"
        ).fetch_all()
    else:
        result = execute_sql(
            state.session,
            f"SELECT * from Users WHERE Username = '{in_str}'"
        ).fetch_all()
    
    if not result:
        return print_error(f"There is no user with the username or userid '{in_str}'.")
    
    from Console.ConsoleState import StateLoggedIn
    userid, username, *_ = result[0]
    state.parent_change_next(
        StateLoggedIn(
            username,
            userid,
            session=state.session,
            player=state._player
        )
    )
    state.exit()

def print_playlists(result):
    print()
    print("Playlists:")
    print("-"*60)
    for (pid, plname, uid) in result:
        print(f"{pid}. {plname}")
    print("-"*60)    

def show_playlists(state, in_str : str):
    result = execute_sql(
        state.session,
        f'SELECT * from Playlists WHERE UserID = {state._user_id}'
    ).fetch_all()
    print_playlists(result)

def show_playlist_songs(state, in_str : str):
    result = execute_sql(
        state.session,
        f"CALL showPlaylistID({state._pl_id}, {state._user_id})"
    ).fetch_all()
    print_song(result)


@sqlsafe
def create_playlist(state, in_str : str):
    if not in_str:
        return print_error(INVALID_ARGUMENT.format(in_str))

    result = execute_sql(
        state.session,
        f"CALL createPlaylist('{in_str}', {state._user_id})"
    ).fetch_all()[0][0]
    if not result:
        print_error(f"Playlist with the name '{in_str}' already exists.")
    

@sqlsafe
def cd_StateHome(state, in_str : str):
    if not in_str:
        return print_error(INVALID_ARGUMENT.format(in_str))
    
    result = []
    if in_str.isdigit():
        response = execute_sql(
            state.session,
            f"SELECT playlistExists({in_str}, {state._user_id})",
            f"SELECT PlaylistName from Playlists WHERE PlaylistID = {in_str}"
        )
        result = response[0].fetch_all()[0][0]
        in_str = response[1].fetch_all()[0][0]
        print(result, in_str)
    else:
        result = execute_sql(
            state.session,
            f"SELECT playlistExistsName('{in_str}', {state._user_id})"
        ).fetch_all()[0][0]

    if not result:
        return print_error(f"No playlist exists with the name '{in_str}'.")

    from Console.ConsoleState import StatePlaylist
    state.next(
        StatePlaylist(
            state._username,
            state._user_id,
            in_str,
            result,
            session=state.session,
            parent = state._parent,
            player = state._player
        )
    )

@sqlsafe
def cd_StatePlaylist(state, in_str : str):
    if in_str != "..":
        return print_error(INVALID_ARGUMENT.format(in_str))
    
    state.prev()

def print_song(result):
    print()
    print("Songs:")
    print("-"*60)
    for (id, name, album, artist, duration) in result:
        print(f"{str(id)} | {name} | {album} | {artist} | ", end="")
        print(time.strftime("%M:%S", time.gmtime(duration)))
    print("-"*60)


@sqlsafe
def find_song(state, in_str : str):
    result = []
    if not in_str:
        result = execute_sql(
            state.session,
            f"CALL getAllSongs()"
        )
    else:
        result = execute_sql(
            state.session,
            f"CALL getSongInfo('{in_str}')"
        ).fetch_all()
    print_song(result)


@sqlsafe
def find_song_playlist(state, in_str : str):
    if not in_str:
        return print_error(INVALID_ARGUMENT.format(in_str))
    result = execute_sql(
        state.session,
        f"CALL getSongPlaylistInfo('{in_str}',{state._pl_id},{state._user_id})"
    ).fetch_all()
    
    print_song(result)
    
@sqlsafe
def add_song_to_playlist(state, in_str : str):
    if not in_str:
        return print_error(INVALID_ARGUMENT.format(in_str))
    
    result = []
    if not in_str.isdigit():
        result = execute_sql(
            state.session,
            f"CALL getSongInfo('{in_str}')"
        ).fetch_all()
        if len(result) > 1: 
            return print_song(result)
        elif not result:
            return print_error(f"No song with the name '{in_str}' in database.")
        result = result[0]
        
    
    if result:
        id, *_ = result
        in_str = str(id)
    result = execute_sql(
        state.session,
        f"CALL addSongToPlaylist({in_str}, {state._pl_id}, {state._user_id})"
    ).fetch_all()[0][0]
    if not result:
        print_error("Could not add song to playlist.")
    else:
        print("Song successfully added!\n")

def print_artists(result):
    print()
    print("Artists:")
    print("-"*60)
    for (id, name) in result:
        print(f"{id} | {name}")
    print("-"*60)

def print_artists_albums(result):
    name = ""
    print()
    print("Artists:")
    print("-"*60)
    artist_dict = {}
    for (id, artist, album, album_id) in result:
        if id not in artist_dict:
            name = artist
            artist_dict[id] = []
        artist_dict[id].append(f"{album_id} | {album}")
    for songs in artist_dict.values():
        print(f"{id}. {name}:")
        print("-"*(len(str(id))+len(name)+3))
        print(*songs, sep="\n")
    print("-"*60)

@sqlsafe
def get_database_artists(state, in_str : str):
    result = []
    if not in_str:
        result = execute_sql(
            state.session,
            f"SELECT * from Artists"
        ).fetch_all()
        print_artists(result)

    else:
        result = execute_sql(
            state.session,
            f"CALL getArtistAndAlbum('{in_str}')"
        ).fetch_all()
        print_artists_albums(result)
    

@sqlsafe
def create_song(state, in_str : str):
    in_str.split(',')
    if not in_str:
        return print_error(INVALID_ARGUMENT.format(in_str))

def song_playing_info(state, in_str):
    if state._player is None:
        print()
        return print("No song playing.")
    print()
    print(state._player.bar())

@sqlsafe
def play_song(state, in_str : str):
    if not in_str and state._player is not None:
        return state._player.play()
    if not in_str:
        return print_error("No song to play.")
    result = []
    if in_str.isdigit():
        result = execute_sql(
            state.session,
            f"CALL getSongInfoID({in_str})"
        ).fetch_all()
    else:
        result = execute_sql(
            state.session,
            f"CALL getSongInfo('{in_str}')"
        ).fetch_all()
        if len(result) > 1:
            return print_song(result)
    
    if not result:
        return print_error(f"No song with name or id '{in_str}'.")
    
    if state._player is not None:
        state._player.exit()
    state._player = Player(song=result[0])

def quit_munix(state, in_str : str):
    from Console.ConsoleState import StateQuit
    state.parent_change_next(
        StateQuit(
            session=state.session,
            player=state._player
        )
    )
    state.exit()

def print_album(result):
    album_name = result[0][1]
    print()
    print(f"{album_name}: ")
    print("-"*60)
    for (album_id, album, song_id, song, artist, duration) in result:
        print(f"{song_id} | {song} | {artist} | ", end="")
        print(time.strftime("%M:%S", time.gmtime(duration)))
    print("-"*60)

def print_album_names(result):
    print()
    print("Albums:")
    print("-"*60)
    for (id, album, artist) in result:
        print(f"{str(id)} | {album} | {artist}")
    print("-"*60)

@sqlsafe
def get_album_songs(state, in_str : str):
    if not in_str:
        return print_error(INVALID_ARGUMENT.format(in_str))
    
    result = []
    if in_str.isdigit():
        result = execute_sql(
            state.session,
            f"CALL getAlbumID({in_str})"
        ).fetch_all()
    else:
        result = execute_sql(
            state.session,
            f"CALL getAlbumName('{in_str}')"
        ).fetch_all()

        if len(result) > 1:
            return print_album_names(result)
        if result:
            a_id, *_ = result[0]
            result = execute_sql(
                state.session,
                f"CALL getAlbumID({a_id})"
            ).fetch_all()
    
    if not result:
        return print_error(f"No album with the name or id '{in_str}'.")
    
    print_album(result)

def pause_player(state, in_str : str):
    state._player.pause()


def queue_song(state, in_str : str):
    if not in_str and state._player is None:
        return print_song([])
    if not in_str:
        print()
        print(f"Current:", state._player.bar())
        return print_song(state._player.get_queue())
    
    result = []
    if in_str.isdigit():
        result = execute_sql(
            state.session,
            f"CALL getSongInfoID({in_str})"
        ).fetch_all()
    else:
        result = execute_sql(
            state.session,
            f"CALL getSongInfo('{in_str}')"
        ).fetch_all()
        if len(result) > 1:
            return print_song(result)
    
    if not result:
        return print_error(f"No song with the name or id '{in_str}'.")

    if state._player is None:
        state._player = Player(song=result[0])
    else:
        state._player.enqueue(result[0])

def skip_song(state, in_str : str):
    if state._player is None:
        return print_error("There is no song playing.")
    state._player.next()

def prev_song(state, in_str : str):
    if state._player is None:
        return print_error("There is no song playing.")
    state._player.prev()

def show_commands(state, in_str : str):
    print("Available commands:")
    print("-"*60)
    print(*state.commands.keys(), sep=" | ")
    print("-"*60)