import math
import os
import sys
import time
import pygame
from threading import Timer
from typing import Callable
from utils import StartableBackgroundThread

DEFAULT_DURATION = 10 * 60  # 10 minutes
DEFAULT_ALERT_INTERVAL = 5 * 60  # 5 minutes

def get_data():

    print("\n===== Welcome to the Meditation Timer =====")
    print("-------------------------------------------")
    print("POINT TO REMEMBER")
    print("You can set the total duration for your meditation session and the interval for the bell sound.")
    print(f"If you don't enter a time, the default duration of {DEFAULT_DURATION // 60} minutes will be used.")
    print(f"If you don't enter an interval, the default interval of {DEFAULT_ALERT_INTERVAL // 60} minutes will be used.\n")
    print("Keep calm. Happy meditation.")
    print("-------------------------------------------\n")

    while True:
        duration_input = input("Enter total minutes to meditate : ")
        alert_interval_input = input("Enter interval in minutes to ring the bell : ")

        if not duration_input.strip() and not alert_interval_input.strip():
            print("No values entered. Using default values: 10 minutes and 5-minute intervals.")
            confirm = input("Do you want to proceed with default values? (yes/no): ").strip().lower()
            if confirm in ["yes", "y", ""]:
                return DEFAULT_DURATION, DEFAULT_ALERT_INTERVAL
            else:
                continue
        else:
            try:
                duration = int(duration_input) * 60 if duration_input.strip() else DEFAULT_DURATION
                alert_interval = int(alert_interval_input) * 60 if alert_interval_input.strip() else DEFAULT_ALERT_INTERVAL
                return duration, alert_interval
            except ValueError:
                print("Invalid input. Please enter numeric values or press Enter to use default values.")
                continue

total_duration, alert_interval = get_data()

ASSETS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")

class MeditationSession(StartableBackgroundThread):

    def __init__(self, duration: int, alert_interval: int):
        super().__init__()
        self._duration = duration
        self._elapsed_time = 0
        self._alert_interval = alert_interval
        self._alert_thread = None

    def _get_background_task_function(self) -> Callable:
        return self._run_timer

    def _run_timer(self):
        self._display_ascii_art("buddha0.txt")
        time.sleep(3)
        self._display_ascii_art("buddha1.txt")
        time.sleep(4)
        self._display_ascii_art("buddha2.txt")

        PlayBell().start()

        if self._duration == 0:  # Infinite timer
            while True:
                if self._alert_thread is None:
                    self._alert_thread = AlertInterval(self._alert_interval)
                    self._alert_thread.start()

                self._show_time()
                time.sleep(1)
                self._elapsed_time += 1
        else:  # Timed meditation
            while self._duration:
                if self._alert_thread is None:
                    self._alert_thread = AlertInterval(self._alert_interval)
                    self._alert_thread.start()

                self._show_time()
                time.sleep(1)
                self._elapsed_time += 1
                self._duration -= 1
        
        self._display_ascii_art("buddha3.txt")
        print(f"Wow! You meditated for {math.floor(self._elapsed_time / 60)} minutes. Great job!")
        sys.exit()

    def _show_time(self):
        minutes, seconds = divmod(self._duration, 60)
        time_display = '{:02d}:{:02d}'.format(minutes, seconds)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(time_display)

    def _display_ascii_art(self, filename):
        ascii_art_file = os.path.join(ASSETS_DIR, filename)
        with open(ascii_art_file) as file:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(file.read())

class AlertInterval(StartableBackgroundThread):

    def __init__(self, interval: int):
        super().__init__(True)
        self._initial_interval = interval
        self._remaining_time = interval

    def _get_background_task_function(self) -> Callable:
        return self._run_alert_timer

    def _run_alert_timer(self):
        while self._remaining_time:
            if self._remaining_time == 1:
                time.sleep(1)
                PlayBell().start()
                self._remaining_time = self._initial_interval
            time.sleep(1)
            self._remaining_time -= 1

class PlayBell(StartableBackgroundThread):

    def __init__(self):
        super().__init__()
        self._sound_file = os.path.join(ASSETS_DIR, "bell_sound.ogg")

    def _get_background_task_function(self) -> Callable:
        return self._play_sound

    def _play_sound(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self._sound_file)
        pygame.mixer.music.play()

meditation_timer = MeditationSession(total_duration, alert_interval)
meditation_timer.start()
