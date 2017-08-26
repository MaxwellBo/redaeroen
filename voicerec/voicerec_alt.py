import speech_recognition as sr
import re
import time

class RecognitionFailedException(Exception):
    pass

class VoiceRecognizer(object):

    def __init__(self, command_str=None):
        self._recognizer = sr.Recognizer()
        self._recognizer.pause_threshold = 0.5
        self._command_re = re.compile(command_str) if command_str is not None else None

    def listen_for_speech(self):
        print("Listen start")
        with sr.Microphone() as mic:
            audio = self._recognizer.listen(mic, phrase_time_limit=2)

        print("Listen done")
        start_time = time.time()
        try:
            result = self._recognizer.recognize_google_cloud(audio) # credentials_json="D:/UserFiles/Documents/credentials.json"
        except sr.UnknownValueError:
            raise RecognitionFailedException("Could not recognise speech")
        except sr.RequestError:
            raise RecognitionFailedException("Failed to get API result")
        print("Request done in " + str(time.time() - start_time) + "s")
        return result

    def listen_for_command(self,):
        while True:
            
            speech = self.listen_for_speech()
            
            
            if self._command_re is None or re.search(self._command_re, speech):
                return speech

if __name__ == '__main__':
    vr = VoiceRecognizer()

    while True:
        try:
            command = vr.listen_for_command()
            print("Command: " + command)
        except RecognitionFailedException as e:
            print("Recognition failed: " + str(e))
