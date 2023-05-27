from Console.console_commands import *
from mysqlx.connection import Session

class State:
    def __init__(self, *, session : Session, parent=None, player = None) -> None:
        self._prev : State = self
        self._next : State = self
        self._substate : State | None = None
        self._player = player
        self._parent : State | None = parent
        self.session = session
        self.commands = {}
        self.print = ""
        self.path = "Munix"
    
    def _input_safe(self, in_str):
        if in_str in ALL_COMMANDS:
            print(f"Command '{in_str}' cannot be used here.")
        else:
            self._input(in_str)

    def _input(self, in_str):
        pass

    def parent_change_next(self, new_state):
        self.get_parent()[-1].next(new_state)
    
    def next(self, new_state):
        new_state._prev = self
        self._next = new_state
    
    def prev(self):
        self._prev._next = self._prev
        self._next = self._prev
    
    def traverse(self):
        return self._next
    

    def _parent_traverse(self):
        if self._parent is None:
            return []
        return [self._parent] + self._parent.get_parent()

    def get_parent(self):
        return [self] + self._parent_traverse()

    def exit(self):
        if self._parent is not None:
            self._next = None
    
    def handle_command(self, in_str : str): 
        cmd, *s = in_str.split(' ', 1)
        string = "" if not s else s[0]
        if cmd in self.commands:
            return self.commands[cmd](self, string)
        return self._input_safe(in_str)
    
    def console(self):
        # Check recursion
        if self._substate is not None:
            self._substate.console()
            self._substate = self._substate.traverse()
        else:
            if self.print:
                print(self.print)
            try:
                self.handle_command(input(self.path+">"))
            except KeyboardInterrupt:
                print()
                self.parent_change_next(
                    StateQuit(
                        session=self.session,
                        player=self._player
                    )
                )
        return self

class StateNotLoggedIn(State):
    def __init__(self, *, session, parent=None, player=None) -> None:
        super().__init__(session=session, parent=parent, player=player)

        self._substate = StateSelectUser(session=session, parent=self)


class StateQuit(State):
    def __init__(self, *, session: Session, parent=None, player=None) -> None:
        super().__init__(session=session, parent=parent, player=player)
        if self._player is not None:
            self._player.exit()


class StateSelectUser(State):
    def __init__(self, *, session, parent=None, player=None) -> None:
        super().__init__(session=session, parent=parent, player=player)
        
        self.path += "/SelectUser"
        self.commands = {
            "ls" : show_users,
            "mkuser" : mkuser_SelectUser,
            "cd" : select_user,
            "quit" : quit_munix,
            "help" : show_commands
        }
        


class StateLoggedIn(State):
    def __init__(self,username, user_id, *, session: Session, parent=None, player=None) -> None:
        super().__init__(session=session, parent=parent, player=player)
        self._user_id = user_id
        self._username = username
        self._substate = StateHome(username, user_id, session=session, parent=self, player=player)

class StateHome(State):
    def __init__(self, username, user_id, *, session: Session, parent=None, player=None) -> None:
        super().__init__(session=session, parent=parent, player=player)
        self._username = username
        self._user_id = user_id
        self.path += f"/{username}"
        self.commands = {
            "ls" : show_playlists,
            "mkplaylist" : create_playlist,
            "cd" : cd_StateHome,
            "song" : find_song,
            "artist" : get_database_artists,
            "mksong" : create_song,
            "playing" : song_playing_info,
            "play" : play_song,
            "quit" : quit_munix,
            "album" : get_album_songs,
            "help" : show_commands,
            "pause" : pause_player,
            "queue" : queue_song,
            "skip" : skip_song,
            "prev" : prev_song
        }
    
class StatePlaylist(State):
    def __init__(self, username, user_id, pl_name, pl_id, *, session: Session, parent=None, player=None) -> None:
        super().__init__(session=session, parent=parent, player=player)
        self._username = username
        self._user_id = user_id
        self._pl_name = pl_name
        self._pl_id = pl_id
        self.path += f"/{username}/{pl_name}"
        self.commands = {
            "ls" : show_playlist_songs,
            "cd" : cd_StatePlaylist,
            "ishere" : find_song_playlist,
            "add" : add_song_to_playlist,
            "song" : find_song,
            "artist" : get_database_artists,
            "playing" : song_playing_info,
            "play" : play_song,
            "quit" : quit_munix,
            "album" : get_album_songs,
            "help" : show_commands,
            "pause" : pause_player,
            "queue" : queue_song,
            "skip" : skip_song,
            "prev" : prev_song
        }
        


        
    
