import argparse
import os
import queue
import sys
import webbrowser
import psutil

import pyautogui
import pyttsx3 as tts
import sounddevice as sd
import time
import vosk

engine = tts.init()
engine.setProperty('rate', 125)

discord_path = "C://Users/Bastek/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Discord Inc/Discord.lnk"
wallpaper_path = "C://Users/Bastek/Desktop/Wallpaper Engine.url"
spotify_path = "C://Users/Bastek/Desktop/Spotify.lnk"
q = queue.Queue()

open_chat = ['jarvis open chat application', 'jarvis open to the obligation', 'jerry open to the obligation',
             'jarvis open to the application', 'jarvis opened an obligation']

close_chat = ['jarvis close to the application', 'jarvis close chat application', 'job these close chat application',
              'jeremy close chat application', 'jarvis close to the obligation']

open_browser = ['jarvis open browser', 'jarvis open the browser', 'jarvis open in browser']

close_browser = ['jarvis close browser', 'jarvis up and browser', 'jarvis close browse at all', 'jerry close the browser',
                 'japanese close the browser']
shut_down = ['jarvis shut down', 'jarvis shut them', 'jarvis to shut down', 'jarvis top down']


def check_if_running(processname):
    for proc in psutil.process_iter():
        try:
            if processname.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def check_if_exists(txt, ls):
    if any(match in txt for match in ls):
        return True
    else:
        return False


def speak(txt):
    engine.say(txt)
    engine.runAndWait()


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

    with sd.RawInputStream(samplerate=args.samplerate, blocksize=8096, device=args.device, dtype='int16',
                           channels=1, callback=callback):
        # print('#' * 80)
        # print('Press Ctrl+C to stop the recording')
        # print('#' * 80)
        speak("Miło cię znowu słyszeć Sir")
        rec = vosk.KaldiRecognizer(model, args.samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                res = rec.Result()
                print(res)

                if check_if_exists(res, open_chat):
                    speak("Uruchamiam Discorda")
                    os.startfile(discord_path)

                if check_if_exists(res, close_chat):
                    speak("Zamykam Discorda")
                    os.system("TASKKILL /F /IM discord.exe")

                if check_if_exists(res, open_browser):
                    speak("Otwieram przeglądarkę")
                    webbrowser.open('https://www.google.com/', new=1)

                if "jarvis open youtube" in res:
                    speak("Otwieram Youtube")
                    webbrowser.open('https://www.youtube.com/', new=1)

                if check_if_exists(res, close_browser):
                    speak("Zamykam przeglądarkę")
                    os.system("TASKKILL /F /IM firefox.exe")

                if check_if_exists(res, shut_down):
                    speak("Wyłączam komputer")
                    os.system("shutdown /s /t 60")
                    if check_if_running("Spotify"):
                        os.system("TASKKILL /F /IM spotify.exe")
                    if check_if_running("Discord"):
                        os.system("TASKKILL /F /IM discord.exe")
                    if check_if_running("firefox"):
                        os.system("TASKKILL /F /IM firefox.exe")
                    if check_if_running("iCUE"):
                        os.system("TASKKILL /F /IM icue.exe")

                if "jarvis next" in res:
                    speak("Następny utwór")
                    pyautogui.press('nexttrack')

                if "jarvis previous" in res:
                    speak("Poprzedni utwór")
                    pyautogui.press('prevtrack', presses=2)

                if "jarvis repeat" in res:
                    speak("Od nowa")
                    pyautogui.press('prevtrack')

                if "jarvis stop" in res:
                    speak("Zatrzymuje")
                    pyautogui.press('playpause')

                if "jarvis play" in res:
                    if check_if_running("Spotify"):
                        speak("Wznawiam")
                        pyautogui.press('playpause')
                    else:
                        speak("Uruchamiam Spotify")
                        os.startfile(spotify_path)
                        time.sleep(5)
                        speak("Wznawiam Słuchanie")
                        pyautogui.press('playpause')

                if "jarvis more volume" in res:
                    for x in range(5):
                        pyautogui.press('volumeup')

                if "jarvis less volume" in res:
                    for x in range(5):
                        pyautogui.press('volumedown')

                if "jarvis sleep" in res:
                    speak("Zasypiam")
                    time.sleep(5)
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

                if "jarvis wallpaper" in res:
                    speak("Restartuje Wallpapera")
                    os.system("TASKKILL /F /IM wallpaper64.exe")
                    time.sleep(5)
                    os.startfile(wallpaper_path)

                if "thanks" in res:
                    speak("No problem Sir")

                if "jarvis shut up" in res:
                    speak("Się robi Sir")
                    parser.exit(0)

            if dump_fn is not None:
                dump_fn.write(data)

except KeyboardInterrupt:
    print('\nDone')
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
