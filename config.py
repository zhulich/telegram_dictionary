import os

import mysql.connector
from dotenv import load_dotenv
from telegram import KeyboardButton

load_dotenv()

# Telegram token
API_TOKEN = os.getenv("API_TOKEN")

# MySQL settings
USER_NAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# connection to DB
cnx = mysql.connector.connect(
    user=USER_NAME, password=PASSWORD, host=DB_HOST, database=DB_NAME
)


# SQL statements
MAX_RATING = "SELECT MAX(rating) FROM eng_ua WHERE user_id = %s"
INSERT = "INSERT INTO eng_ua (english, ukraine, user_id) VALUES (%s, %s, %s)"
SELECT = (
    "SELECT english, ukraine FROM eng_ua WHERE user_id = %s and rating >= %s LIMIT 20"
)
SELECT_NEWEST = (
    "SELECT english, ukraine FROM eng_ua WHERE user_id = %s ORDER BY pk DESC LIMIT 10"
)
SELECT_ENG = "SELECT english FROM eng_ua WHERE user_id = %s"
SELECT_UA = "SELECT ukraine FROM eng_ua WHERE user_id = %s"
SELECT_LIMIT = "SELECT english, ukraine FROM eng_ua WHERE (user_id = %s) LIMIT 4"
RATING_ZERO = (
    "UPDATE eng_ua SET rating = 0 WHERE english = %s and ukraine = %s and user_id = %s"
)
RATING_INCREASE = "UPDATE eng_ua SET rating = rating + 1"

# Commands for choosing part of speech
commands = [
    "nouns",
    "adverbs",
    "adjectives",
    "prepositions",
    "verbs",
    "compound-words",
    "Remind in 15 minutes",
    "Back to main menu",
]

# URLs for parsing and translation
random_words_url = "https://www.randomlists.com/data/%s.json"
deepl_url = "https://www.deepl.com/translator#en/uk/%s"

# Buttons for bot keyboard
buttons_start = [
    [KeyboardButton("Add new word"), KeyboardButton("Repeat words")],
    [KeyboardButton("Get poll"), KeyboardButton("Setup daily events")],
]
buttons_speech_parts = [
    [KeyboardButton(commands[0]), KeyboardButton(commands[1])],
    [KeyboardButton(commands[2]), KeyboardButton(commands[3])],
    [KeyboardButton(commands[4]), KeyboardButton(commands[5])],
    [KeyboardButton(commands[6]), KeyboardButton(commands[7])],
]
buttons_poll = [
    [KeyboardButton("ukraine")],
    [KeyboardButton("english")],
    [KeyboardButton(commands[-1])],
]
