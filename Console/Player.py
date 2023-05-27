from threading import Thread
from threading import Lock
import time

LINE_UP = '\033[1F'
LINE_DOWN = '\033[1E'
LINE_RIGHT = "\033[100F"
LINE_CLEAR = '\x1b[2K'

class Player:
    def __init__(self, *, song) -> None:
        self.song = song
        self._playing = True
        self.queue = [song]
        self.elapsed = 0
        self._active = True
        self._lock = Lock()
        self.qp = 0
        self._thread = Thread(target=self._player_clock).start()

    def __del__(self):
        if self._active:
            self._active = False
            try:
                self._lock.release()
            except Exception:
                pass

    def _pause_audio(self):
        pass

    def _play_audio(self):
        pass

    def get_queue(self):
        return_lst = []
        if self.qp + 1 < len(self.queue):
            return_lst = self.queue[self.qp:]
        return return_lst

    def enqueue(self, song):
        self.queue.append(song)

    def exit(self):
        self._active = False
        try:
            self._lock.release()
        except Exception:
            pass


    def pause(self):
        if self._playing:
            self._playing = False
            self._lock.acquire()

    def play(self):
        if not self._playing:
            self._playing = True
            self._lock.release()
            self._play_audio()
    
    def elapse(self, t_sec):
        self.elapsed += t_sec
        
    def next(self):
        self.elapsed = 0
        if self.qp + 1 != len(self.queue) and self.queue:
            self.qp += 1
            self.song = self.queue[self.qp]

    def prev(self):
        self.elapsed = 0
        if self.qp == 0:
            return
        self.qp -= 1
        self.song = self.queue[self.qp]



    def _player_clock(self):
        while self._active:
            if self._lock.locked():
                self._pause_audio()
                self._lock.acquire()
                self._lock.release()
            time.sleep(0.1)
            self.elapse(0.1)
            *_, duration = self.song
            if(self.elapsed > duration):
                self.next()
                

    def bar(self):
        if not self.song:
            return "No song is playing."
        (id, song, album, artist, duration) = self.song
        dt = time.strftime("%M:%S", time.gmtime(duration))
        et = time.strftime("%M:%S", time.gmtime(self.elapsed))
        return f"♫  '{song}' - {artist}    {et}/{dt}"

            
        