import sys
import pyaudio

from six.moves import queue

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

class MicGen(object):
    def __init__(self, rate, chunk_size):
        self._rate = rate
        self._chunk_size = chunk_size
        self._buffer = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(channels=1, 
                                                        rate=self._rate, input=True, 
                                                        frames_per_buffer=self._chunk_size, 
                                                        stream_callback=self._fill_buffer)
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frames, time_info, status):
        self._buffer.put(in_data)
        return None, pyaudio.paContinue

    def get_rate(self):
        return self._rate

    def get_chunk_size(self):
        return self._chunk_size

    def generator(self):
        while not self.closed:
            chunk = self._buffer.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buffer.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield ''.join(data)


class VoiceRecogniser(object):

    def __init__(self, input_stream):
        self._input_stream = input_stream
        self._client = speech.SpeechClient()
        self._speech_config = types.RecognitionConfig(
                                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                                sample_rate_hertz=input_stream.get_rate(),
                                language_code='en-AU')
        self._streaming_config = types.StreamingRecognitionConfig(
                                config=self._speech_config,
                                interim_results=False
        )

    def generator(self):
        requests = (types.StreamingRecognitionRequest(audio_content=content) 
                    for content 
                    in self._input_stream.generator())
        
        responses = self._client.streaming_recognize(self._streaming_config, requests)

        for response in responses:
            pass

