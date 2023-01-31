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
    if command == "Nouns":
        words = [f"the {word}" for word in words]
    if command == "Verbs":
        words = [f"to {word}" for word in words]
    await save_in_db(words, user_id)

    result = []
    for word in words:
        translation = translator.translate(word, dest="uk")
        result.append(f"{word.split(' ')[1]} - {translation.text}")

    return "\n".join(result)


async def save_in_db(words: list[str], user_id: int) -> None:
    translator = Translator(service_urls=["translate.googleapis.com"])
    save = (
        (word.split(" ")[1], translator.translate(word, dest="uk").text, user_id)
        for word in words
    )
    for pair in save:
        await add_new_pair(pair)
