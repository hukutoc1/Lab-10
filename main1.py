import json, time, requests
import pyttsx3, pyaudio, vosk

url = 'https://wttr.in/Saint-Petersburg?format=2'
direction = {'↑': 'южный',
             '↓;': 'северный',
             '→': 'западный',
             '←': 'восточный'
             }


class Speech:
    def __init__(self):
        self.speaker = 0
        self.tts = pyttsx3.init('sapi5')

    def set_voice(self, speaker):
        self.voices = self.tts.getProperty('voices')
        for count, voice in enumerate(self.voices):
            if count == 0:
                # print('0')
                id = voice.id
            if speaker == count:
                id = voice.id
        return id

    def text2voice(self, speaker=0, text='?????'):
        self.tts.setProperty('voice', self.set_voice(speaker))
        self.tts.say(text)
        self.tts.runAndWait()


class Recognize:
    def __init__(self):
        model = vosk.Model(
            r'D:\Download\vosk-model-small-ru-0.22\vosk-model-small-ru-0.22')
        self.record = vosk.KaldiRecognizer(model, 16000)
        self.stream()

    def stream(self):
        pa = pyaudio.PyAudio()
        self.stream = pa.open(format=pyaudio.paInt16,
                              channels=1,
                              rate=16000,
                              input=True,
                              frames_per_buffer=8000)

    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.record.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.record.Result())
                if answer['text']:
                    yield answer['text']


def speak(text):
    speech = Speech()
    speech.text2voice(speaker=3, text=text)


rec = Recognize()
text_gen = rec.listen()
rec.stream.stop_stream()
speak('Здравствуйте')
time.sleep(0.5)
rec.stream.start_stream()
for text in text_gen:
    if text == 'завершить':
        speak('Бывай, Ихтиандр')
        exit()
    elif text == "температура":
        req = requests.get(url)
        row = req.text.split()[1]
        row = row[1:row.index('°')] + " градусов"
        speak(row)
        print(row)
    elif text == "ветер":
        req = requests.get(url)
        row = req.text.split()[2]
        result = ''.join(
            list(filter(lambda x: x.isdigit(), row))) + " " + 'км/ч'
        speak(result)
        print(result)
    elif 'направление' in text:
        req = requests.get(url)
        row = req.text.split()[2][2]
        result = direction[row] + ' ветер'
        print(result)
        speak(result)
    elif text == 'гулять':
        req = requests.get(url)
        row = req.text.split()
        if int(row[1][2: row[1].index('°')]) > 5 and row[1][2] == '+' and int(
                ''.join(list(filter(lambda x: x.isdigit(), row[2])))) < 15:
            result = 'рекомендую'
        else:
            result = 'не рекомендую'
        print(result)
        speak(result)
    else:
        print(text)
