import speech_recognition as sr

import synthesis_service as syn


class SpeechToTextService:
    _instance = None

    def __init__(self):
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()
        self.syn = syn.synthesis_service()

    def speech_to_text(self):
        text = ""
        print("Минутку тишины, пожалуйста...")
        with self._microphone as source:
            self._recognizer.adjust_for_ambient_noise(source)
            self.syn.speak_enter_word()
        with self._microphone as source:
            audio = self._recognizer.listen(source)
        self.syn.speak_control_word()  # отклик от ассистента, завешающий взаимодействие

        # Распознавание речи на серверах Google
        try:
            text = self._recognizer.recognize_google(audio, language="ru_RU")
        except sr.UnknownValueError:
            print("Фраза не выявлена")
        except sr.RequestError as e:
            print("Не могу получить данные от сервиса Google Speech Recognition; {0}".format(e))
        text = text.lower()
        return text


def speech_to_text_service():
    if SpeechToTextService._instance is None:
        SpeechToTextService._instance = SpeechToTextService()
    return SpeechToTextService._instance
