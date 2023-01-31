# Telegram Bot

Telegram bot that help you with learning english, send you new words and remind its.

https://t.me/eng_word_book_bot

## Installation

```bash
git clone git@github.com:zhulich/telegram_dictionary.git
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# be careful, googletrans and python telegram bot use different versions of httpx, 
# so when you install requirements, there will most likely be a dependency conflict.

pip install googletrans 3.0.0
pip install python-telegram-bot 20.0
pip install httpx==0.23.3

# now go to the indicated path and open it env/lib/python3.10/site-packages/googletrans/client.py, 
# in line 55 change "SyncHTTPTransport" to "AsyncHTTPProxy"
```

## Features
-Manual addition of words with their translation.

-Every day, at the time specified by the user, the bot sends 10 words with a translation, saves them to the dictionary.

-Each time, you choose words from which part of speech to get.

-The bot sends the last 10 learned words every morning and evening.

-You can set the time when the bot will send new words and remind them.

-Every day, the bot increases the rating of all words by one.

-You can ask the bot to remind  words, in which case it will send 5 random words with the highest rating. Resets the rating.

-You can choose a quiz where you will need to indicate the correct translation of an English or Ukrainian word. Resets the rating.


## Future features
-Replacing the translation from English to Ukrainian with the definition of the concept.
-Examples of using words in a sentence.