from gtts import gTTS
from gtts.tts import gTTSError
from pydub import AudioSegment
from pydub import playback
from io import BytesIO
from multiprocessing import Process, Queue
import time
import json
import uuid
import os

class ttsPlayer:
    cacheFolder = './cache/'
    cacheFile = cacheFolder + 'voiceCache.json'
    que = None
    thread = None
    def __init__(self):
        if not os.path.exists(self.cacheFolder):
            os.makedirs(self.cacheFolder)
        if not self.que:
            self.que = Queue()
        if not self.thread:
            self.thread = Process(target=self.__worker)
            self.thread.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
            self.thread.start()

    class NetworkErrorException(Exception):
        pass

    def __worker(self):
        try:
            while True:
                try:
                    text = self.que.get(timeout=1)
                    if text == None: #This is our que to exit the worker thread.
                        return
                except Exception as e:
                    pass
                else:
                    mp3Filename = self.__getMp3(text)
                    with open(mp3Filename, 'rb') as f:
                        song = AudioSegment.from_file(f, format='mp3')
                    print(f"Playing: {text}")
                    playback.play(song)
        except KeyboardInterrupt as e:
            return # exit the process

    def __getMp3(self, text):
        try:
            with open(self.cacheFile, 'r') as voiceCache_fp:
                cache = json.load(voiceCache_fp)
        except FileNotFoundError:
            cache = {}
        if text not in cache:
            # download and save the mp3
            mp3_fp = BytesIO()
            try:
                self.tts = gTTS(text, lang='en')
                self.tts.write_to_fp(mp3_fp)
            except gTTSError as error:
                print(f"Network error occurred: {error}")
                raise self.NetworkErrorException
            mp3_fp.seek(0)
            mp3Filename = self.cacheFolder + str(uuid.uuid4()) + '.mp3'
            with open(mp3Filename, 'wb+') as f:
                f.write(mp3_fp.getbuffer())
            cache[text] = mp3Filename
            with open(self.cacheFile, 'w+') as voiceCache_fp:
                json.dump(cache, voiceCache_fp)
            print(f"*******Caching new string: '{text}' --> {mp3Filename}")
        else:
            print(f"*******Found '{text}' as {cache[text]}")
        return cache[text]

    def quePlayback(self, text: str):
        # download (if needed) in the current thread
        self.voiceCacheAdd(text)
        # but play in the background thread
        self.que.put(text)

    def stop(self):
        self.que.put(None) #poison pill
        self.thread.join()

    def voiceCacheAdd(self, text: str):
        self.__getMp3(text)

if __name__ == "__main__":
    # Basic tests
    tts = ttsPlayer()
    try:
        tts.voiceCacheAdd('one')
        tts.voiceCacheAdd('one')
        tts.voiceCacheAdd('two')
        tts.quePlayback('one')
        tts.quePlayback('two')
        tts.quePlayback('three')
        time.sleep(5)
        tts.quePlayback('four')
        tts.stop()
    except ttsPlayer.NetworkErrorException:
        print(f"Network error")
