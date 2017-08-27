import sys
import pyaudio
import re
import time

import queue

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
        self.i = 0

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
            self.i += 1
            # print(f'Yield: {self.i}')
            yield b''.join(data)


class VoiceRecogniser(object):

    def __init__(self, input_stream, command_phrase=None):
        self._input_stream = input_stream
        self._client = speech.SpeechClient()
        self._speech_config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=input_stream.get_rate(),
            language_code='en-AU')
        self._streaming_config = types.StreamingRecognitionConfig(
            config=self._speech_config,
            single_utterance=False,
            interim_results=False
        )
        if command_phrase is None:
            self._command_phrase = None
        else:
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

        return transcript, result.is_final

    def _process_response_final(self, response):
        (transcript, is_final) = self._process_response(response)

        if is_final:
            # Check for the command phrase
            if self._command_phrase is not None and not re.search(self._command_phrase, transcript):
                return None
            return transcript
        else:
            return None

    def generator_all(self):
        while True:
            t = time.time()
            response = next(self._responses)
            print("REQUEST TOOK: " + str(time.time() - t))
            if response is None:
                continue

            try:
                transcript, is_final = self._process_response(response)
            except TypeError:
                continue

            if transcript is not None:
                yield transcript, is_final

    def generator_final(self):
        while True:
            response = next(self._responses)
            transcript = self._process_response_final(response)

            if transcript is not None:
                yield transcript


def voice_recognition_generator():
    with MicGen(16000, int(16000/10)) as stream:
        while True:
            vr = VoiceRecogniser(stream)
            try:
                for command, is_final in vr.generator_all():
                    yield command, is_final
            except grpc._channel._Rendezvous:
                continue


def voice_command_generator(command_str: str = None):
    with MicGen(16000, int(16000/20)) as stream:
        while True:
            vr = VoiceRecogniser(stream, command_str)
            # Print things out
            try:
                for command in vr.generator_final():
                    yield command
            except grpc._channel._Rendezvous:
                continue


if __name__ == '__main__':
    for c in voice_command_generator('hey google'):
        print("COMMAND: " + c)
