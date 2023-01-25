from random import choice
import requests
from googletrans import Translator

from config import random_words_url
from cursors import get_all_eng_words, add_new_pair


def parse(command: str) -> list:
    r = requests.get(random_words_url % (command,))
    return r.json()["data"]


async def google_translate(command: str, user_id: int) -> str:
    translator = Translator(service_urls=["translate.googleapis.com"])
    db_words = await get_all_eng_words((user_id,))
    parsed = parse(command)
    words = []
    while len(words) < 9 or not parsed:
        word = choice(parsed)
        if word not in db_words:
            words.append(word)
        parsed.remove(word)
    if command == "nouns":
        words = [f"the {word}" for word in words]
    if command == "verbs":
        words = [f"to {word}" for word in words]
    result = []
    for word in words:
        translation = translator.translate(word, dest="uk")
        result.append(f"{word.split(' ')[1]} - {translation.text}")
    save_in_db = (
        (word.split(" ")[1], translator.translate(word, dest="uk").text, user_id) for word in words
    )

    for char in save_in_db:
        await add_new_pair(char)

    return "\n".join(result)
