import ctypes
import speech_recognition as sr
import pyautogui
import webbrowser
import re
import random
import pyttsx3
import subprocess
import urllib.request
import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys
import winsound
import time
from plyer import notification
from word2number import w2n
import screen_brightness_control as sbc
from pynput.keyboard import Key, Controller
import datetime
import pyjokes
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, QTime, QDate, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from edithUi import Ui_edithUi

speech = sr.Recognizer()  # decrease the surrounding voice


# ********************************************************************************
q = queue.Queue()


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-f', '--filename', type=str, metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-m', '--model', type=str, metavar='MODEL_PATH',
    help='Path to the model')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)

try:
    if args.model is None:
        args.model = "model"
    if not os.path.exists(args.model):
        print("Please download a model for your language from https://alphacephei.com/vosk/models")
        print("and unpack as 'model' in the current folder.")
        parser.exit(0)
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])

    model = vosk.Model(args.model)

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

except KeyboardInterrupt:
    print('\nDone')
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))



# ***************************************************************************
try:
    engine = pyttsx3.init()  # init -initialize
except ImportError:
    print('Requested driver is not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')
# for voice in voices:
#     print(voice.id)

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')
engine.runAndWait()


# ********************************************************************

class MainThread(QThread):
    def __init__(self):
        super(MainThread, self).__init__()

    def run(self):
        self.TaskExecution()

    # class gui():
    #     value = (420, 340)

    def starts(self):
        pyautogui.click(420, 340)


    def speak_text_cmd(self,cmd):
        engine.say(cmd)
        engine.runAndWait()


    # def play_sound(self,mp3_list):
    #     mp3 = random.choice(mp3_list)
    #     play_sound(mp3)


    def switch_window(self):
        k = Controller()
        k.press(Key.alt)
        k.press(Key.tab)
        k.release(Key.alt)
        k.release(Key.tab)


    def wish(self):
        h = int(datetime.datetime.now().hour)
        if 0 <= h < 12:
            self.speak_text_cmd("good morning, how can i help you")
        elif 12 <= h < 18:
            self.speak_text_cmd("good afternoon, how can i help you")
        elif 18 <= h < 21:
            self.speak_text_cmd("good evening, how can i help you")
        else:
            self.speak_text_cmd("good night, how can i help you")


    def connect(self,host='https://www.google.co.in/'):
        try:
            urllib.request.urlopen(host)  # Python 3.x
            return True
        except:
            return False

    # ************************ READ VOICE FUNCTION ********************************
    def read_voice_cmd(self):
        if self.connect():
            voice_text = ''
            with sr.Microphone() as source:
                print('Listening.....')
                speech.pause_threshold = 1
                audio = speech.listen(source, timeout=10, phrase_time_limit=5)

            try:
                voice_text = speech.recognize_google(audio, language='en-in')
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print('Network error')
            except sr.WaitTimeoutError:
                pass

            return voice_text

        else:
            with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000, device=args.device, dtype='int16',
                                channels=1, callback=callback):
                print("Listening.....")

                rec = vosk.KaldiRecognizer(model, args.samplerate)
                while True:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        a = rec.Result()
                        b = a.split('"')
                        return b[3]
                    else:
                        continue


# ********************** MAIN FUNCTION *****************************
    def TaskExecution(self):
        self.speak_text_cmd('I am EDITH your personal assistant, how can i help you')
        while True:
            self.voice_note = self.read_voice_cmd()
            self.voice_note = self.voice_note.lower()
            print('cmd : {}'.format(self.voice_note))
            
            if 'hai' in self.voice_note or 'hi' in self.voice_note:
                self.wish()
                continue
            
            elif 'hello' in self.voice_note:
                self.speak_text_cmd('Oh hi! Good to see you')
                continue

            elif 'tell me about yourself' in self.voice_note:
                self.speak_text_cmd("I am EDITH your personal assistant, I'm here to help you. Let me know if you need anything.")
                continue

            elif 'jokes' in self.voice_note or 'tell jokes' in self.voice_note:
                joke = pyjokes.get_joke(language="en", category="neutral")
                self.speak_text_cmd(joke)
                continue

            elif 'open facebook' in self.voice_note:
                url = 'https://www.facebook.com/'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue

            elif 'open instagram' in self.voice_note:
                url = 'https://www.instagram.com/'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue

            elif 'open github' in self.voice_note:
                url = 'https://github.com/'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue

            elif 'open linkedin' in self.voice_note:
                url = 'https://in.linkedin.com/'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue

            elif 'open telegram' in self.voice_note:
                url = 'https://telegram.org/'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue

            elif 'open whatsapp' in self.voice_note:
                url = 'https://web.whatsapp.com/'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue

            elif 'open discord' in self.voice_note:
                url = 'https://discord.com/'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue

            elif 'open google meet' in self.voice_note:
                url = 'https://meet.google.com/'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue

            elif 'open google drive' in self.voice_note:
                url = 'https://drive.google.com/drive/my-drive'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue
            
            elif 'open google' in self.voice_note:
                url = 'https://www.google.co.in/'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue

            elif 'open gmail' in self.voice_note:
                url = 'https://www.google.com/gmail/'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue

            elif 'open youtube' in self.voice_note:
                url = 'https://www.youtube.com/'
                webbrowser.open(url)
                self.speak_text_cmd('sure')
                continue

            elif 'open calculator' in self.voice_note:
                subprocess.Popen('C:\\Windows\\System32\\calc.exe')
                self.speak_text_cmd('sure')
                continue

            elif 'open notepad' in self.voice_note:
                subprocess.Popen('C:\\Windows\\System32\\notepad.exe')
                self.speak_text_cmd('sure')
                continue

            elif 'open command prompt' in self.voice_note:
                os.system('start cmd')
                self.speak_text_cmd('sure')
                continue

            elif 'clear terminal' in self.voice_note:
                os.system('cleart')
                self.speak_text_cmd('sure')
                continue

            elif 'log out my' in self.voice_note:
                for value in ['pc', 'computer', 'system', 'laptop', 'machine']:
                    ctypes.windll.user32.LockWorkStation()
                self.speak_text_cmd("take a break")
                continue

            elif 'shutdown my' in self.voice_note:
                for value in ['pc', 'computer', 'system', 'laptop', 'machine']:
                    os.system("shutdown -s")
                continue

            elif 'restart my' in self.voice_note:
                for value in ['pc', 'computer', 'system', 'laptop', 'machine']:
                    os.system("shutdown /r /t 1")
                continue

            elif 'play song' in self.voice_note or 'play music' in self.voice_note:
                self.speak_text_cmd('which song: ')
                song = self.read_voice_cmd()
                reg_ex = re.search('open youtube (.*)', song)
                url = ('https://www.youtube.com/results?search_query=' + song + '%2F')
                webbrowser.open(url)
                self.speak_text_cmd('here we go')
                self.speak_text_cmd("do you want to play")
                continue

            elif 'play it' in self.voice_note or 'play' in self.voice_note or 'pause' in self.voice_note:
                self.starts()
                continue

            elif 'open wikipedia' in self.voice_note:
                self.speak_text_cmd('on which topic:')
                topic = self.read_voice_cmd()
                reg_ex = re.search('open wikipedia (.*)', topic)
                url = ('https://en.wikipedia.org/wiki/' + topic)
                webbrowser.open(url)
                self.speak_text_cmd('here is the information about' + topic)
                continue

            elif 'adjust brightness' in self.voice_note:
                self.speak_text_cmd('provide brightness percentage')
                level = self.read_voice_cmd()
                sbc.set_brightness(level)
                self.speak_text_cmd('sure')
                continue
            
            elif 'increase volume' in self.voice_note:
                pyautogui.press('volumeup')
                self.speak_text_cmd('sure')
                continue
            
            elif 'decrease volume' in self.voice_note:
                pyautogui.press('volumedown')
                self.speak_text_cmd('sure')
                continue
            
            elif 'mute' in self.voice_note or 'mute volume' in self.voice_note:
                pyautogui.press('volumemute')
                self.speak_text_cmd('sure')
                continue
            
            elif 'unmute' in self.voice_note or 'unmute volume' in self.voice_note:
                pyautogui.press('volumeunmute')
                self.speak_text_cmd('sure')
                continue

            elif 'switch window' in self.voice_note:
                self.switch_window()
                self.speak_text_cmd('sure')
                continue

            elif 'locate the city' in self.voice_note:
                self.speak_text_cmd('which city:')
                city = self.read_voice_cmd()
                reg_ex = re.search('locate the city (.*)', city)
                webbrowser.open('https://www.google.com/maps/place/' + city)
                self.speak_text_cmd('sure')
                continue

            elif 'reminder' in self.voice_note:
                def times(reminder, seconds):
                    notification.notify(
                        title="Reminder is set",
                        message=" ",
                        app_icon="C:/Users/admin/Desktop/EDITHGui/reminder1.ico"
                    )
                    time.sleep(seconds)
                    # alarm
                    frequency = 2500
                    duration = 1800
                    for i in range(4):
                        winsound.Beep(frequency, duration)

                    notification.notify(
                        title="Reminder",
                        message=reminder,
                        app_icon="C:/Users/admin/Desktop/EDITHGui/reminder2.ico"
                    )

                self.speak_text_cmd("What's the reminder: ")
                message = self.read_voice_cmd()
                self.speak_text_cmd("Add time in minutes: ")
                second = self.read_voice_cmd()
                sec = w2n.word_to_num(second)
                sec1 = sec * 60
                times(message, sec1)
                continue
            
            elif "take screenshot" in self.voice_note or "screenshot" in self.voice_note:
                self.speak_text_cmd("sir, please tell me the name for this screenshot file")
                name = self.read_voice_cmd().lower()
                self.speak_text_cmd("please hold the screen, i will take screenshot in 3 seconds, ")
                time.sleep(3)
                img = pyautogui.screenshot()
                img.save(f"C:/Users/admin/Pictures/{name}.png")
                self.speak_text_cmd("done!, the screenshot is saved in your pictures folder")
                continue

            elif 'time' in self.voice_note:
                a = datetime.datetime.now()
                a = str(str(a.hour) + 'hours' + str(a.minute) + 'minutes')
                self.speak_text_cmd(f"it is{a}")
                continue

            elif 'google search' in self.voice_note:
                self.speak_text_cmd('on which topic:')
                topic = self.read_voice_cmd()
                reg_ex = re.search('open google (.*)', topic)
                url = ('https://www.google.com/search?q=' + topic)
                webbrowser.open(url)
                self.speak_text_cmd('here is the information about' + topic)
                continue

            elif 'bye' in self.voice_note or 'exit' in self.voice_note:
                self.speak_text_cmd('have a nice day')

                exit()


startExecution = MainThread()

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_edithUi()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.startTask)
        self.ui.pushButton_2.clicked.connect(self.close)

    def startTask(self):
        self.ui.movie = QtGui.QMovie("C:/Users/admin/Desktop/EDITHGui/gui.gif")
        self.ui.label.setMovie(self.ui.movie)
        self.ui.movie.start()
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        startExecution.start()

    def showTime(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        label_time = current_time.toString('hh:mm:ss')
        label_date = current_date.toString(Qt.ISODate)
        self.ui.textBrowser.setText(label_date)
        self.ui.textBrowser_2.setText(label_time)



app = QApplication(sys.argv)
edith = Main()
edith.show()
app.exit(app.exec_())
