import pyttsx3
from random import randint
from resources import configuration as conf
from resources import my_enum


class SynthesisService:
    _instance = None

    def __init__(self):
        self.tts = pyttsx3.init()
        self.tts.setProperty('voice', 'ru')
        self.tts.setProperty('voice', conf.PATH_TO_VOICE_DRIVE)

    def speak_enter_word(self):  # произнести отклик
        random = randint(0, 2)
        self.tts.say(my_enum.enter_words[random])
        self.tts.runAndWait()

    def speak_control_word(self):  # произнести отклик, завешающий взаимодействие с пользователем
        random = randint(0, 2)
        self.tts.say(my_enum.control_words[random])
        self.tts.runAndWait()

    def speak(self, text):  # произнести произвольную фразу
        self.tts.say(text)
        self.tts.runAndWait()


def synthesis_service():
    if SynthesisService._instance is None:
        SynthesisService._instance = SynthesisService()
    return SynthesisService._instance
