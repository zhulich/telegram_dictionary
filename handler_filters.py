import re
from datetime import datetime
from telegram import Update
from telegram.ext.filters import UpdateFilter

from config import commands


class EnglishFilter(UpdateFilter):
    def filter(self, update: Update) -> bool:
        return bool(re.search("[a-zA-Z]", update.message.text))


class UkraineFilter(UpdateFilter):
    def filter(self, update: Update) -> bool:
        return bool(re.search("[а-яА-Я]", update.message.text))


class TimeHandler(UpdateFilter):
    def filter(self, update: Update) -> bool:
        try:
            datetime.strptime(update.message.text, "%H:%M").time()
        except ValueError:
            return False
        return True


class SpeechPart(UpdateFilter):
    def filter(self, update: Update) -> bool:
        if update.message.text in commands[:-2]:
            return True
        return False


speech_part_filter = SpeechPart()
time_filter = TimeHandler()
english_filter = EnglishFilter()
ukraine_filter = UkraineFilter()
