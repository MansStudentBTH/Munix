from Console.ConsoleState import StateNotLoggedIn, StateQuit


class Munix:
    def __init__(self, session) -> None:
        self._user = ""
        self._playing = ""
        self.state = StateNotLoggedIn(session=session)
    
    def start_console(self):
        while not isinstance(self.state,StateQuit):
            self.state.console()
            self.state = self.state.traverse()



