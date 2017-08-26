import sys
import pyaudio
import re
import time

from six.moves import queue

import grpc
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
        self._audio_stream = self._audio_interface.open(format=pyaudio.paInt16, channels=1, 
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
            yield b''.join(data)


class VoiceRecogniser(object):

    def __init__(self, input_stream, command_phrase=None):
        self._input_stream = input_stream
        self._client = speech.SpeechClient()
        self._speech_config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=input_stream.get_rate(),
            language_code='en-US')
        self._streaming_config = types.StreamingRecognitionConfig(
            config=self._speech_config,
            single_utterance=False,
            interim_results=False
        )
        self._command_phrase=re.compile(command_phrase, re.I)
        gen = self._input_stream.generator()
        self._requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content
                    in gen)
        self._responses = self._client.streaming_recognize(self._streaming_config, self._requests)

    def _process_response(self, response):
        if not response.results:
            return None

        # Check for multiple results
        result = response.results[0]
        if not result.alternatives[0]:
            return None

        # Get the top alternative
        transcript = result.alternatives[0].transcript

        # Check for the command phrase
        if not re.search(self._command_phrase, transcript):
            return None

        # Only use final results
        if result.is_final: 
            return transcript
        else:
            return None

    def generator(self): 
        while True:
            response = next(self._responses)
            transcript = self._process_response(response)

            if transcript is not None:
                yield transcript


def voice_command_generator(command_str: str = None):
    with MicGen(16000, int(16000/10)) as stream:
        while True:
            vr = VoiceRecogniser(stream, command_str)
            # Print things out
            try:
                for command in vr.generator():
                    yield command
            except grpc._channel._Rendezvous:
                continue

if __name__ == '__main__':
    for c in voice_command_generator('hey google'):
        print("COMMAND: " + c)
