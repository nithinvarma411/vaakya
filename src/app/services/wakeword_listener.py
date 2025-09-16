import pvporcupine
import sounddevice as sd
import numpy as np
import queue

class WakeWordListener:
    def __init__(self):
        # Use "hey google" for a quick test, or add your custom "hey vaakya" keyword if you train it!
        self.porcupine = pvporcupine.create(keywords=["hey vaakya"])
        self.sample_rate = self.porcupine.sample_rate
        self.frame_length = self.porcupine.frame_length
        self.q = queue.Queue()

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.q.put(indata.copy())

    def listen(self):
        with sd.InputStream(channels=1, samplerate=self.sample_rate, dtype='int16',
                            blocksize=self.frame_length, callback=self._audio_callback):
            print("Listening for wake word...")
            while True:
                pcm = self.q.get().flatten()
                result = self.porcupine.process(pcm)
                if result >= 0:
                    print("Wake word detected!")
                    break  # When detected, exit method so caller can start audio collection/transcription

    def cleanup(self):
        self.porcupine.delete()
