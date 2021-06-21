from gtts import gTTS
from pydub import AudioSegment
from pydub import playback
from io import BytesIO
from multiprocessing import Process, Queue
import time

class ttsPlayer:
    que = None
    thread = None
    def __init__(self):
        if not self.que:
            self.que = Queue()
        if not self.thread:
            self.thread = Process(target=self.__worker)
            self.thread.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
            self.thread.start()

    def __worker(self):
        try:
            while True:
                try:
                    text = self.que.get(timeout=1)
                    if text == None: #poison pill; This is our que to exit.
                        return
                except Exception as e:
                    pass
                else:
                    tts = gTTS(text, lang='en')
                    mp3_fp = BytesIO()
                    tts.write_to_fp(mp3_fp)
                    mp3_fp.seek(0)
                    song = AudioSegment.from_file(mp3_fp, format='mp3')
                    #print(f"Playing: {text}")
                    playback.play(song)
        except KeyboardInterrupt as e:
            return # exit the process

    def quePlayback(self, text: str):
        self.que.put(text)

    def stop(self):
        self.que.put(None) #poison pill
        self.thread.join()

if __name__ == "__main__":
    # Basic tests
    tts = ttsPlayer()
    tts.quePlayback("one")
    tts.quePlayback("two")
    tts.quePlayback("three")
    time.sleep(5)
    tts.quePlayback("four")
    tts.stop()
