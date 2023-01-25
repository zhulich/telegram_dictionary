import logging
import random
from datetime import datetime, time

import pytz
from telegram import Update, ReplyKeyboardMarkup, Poll
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from config import commands, buttons_start, buttons_speech_parts, buttons_poll
from cursors import (
    get_all_ua_words,
    get_rating,
    words_with_highest_rating,
    reset_rating,
    add_new_pair,
    increase_rating,
    newest_words,
    get_all_eng_words,
)

from translate import google_translate

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hey, this bot created to help you learn and keep in mind some new words. "
        "Use </info> command to see more information",
        reply_markup=ReplyKeyboardMarkup(buttons_start, resize_keyboard=True),
    )


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Okay, lets go to main menu.",
        reply_markup=ReplyKeyboardMarkup(buttons_start, resize_keyboard=True),
    )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Bot work only with english and ukraine languages.\n\n"
        "It will give you 10 pairs of english and ukraine words at the 14:00, and remind its twice, "
        "first time at 21:00 in the evening and second at 8:00 in the next morning.\n\n"
        "<Setup daily events> change this time, just tap the button and bot will ask you new one.\n\n"
        "<Add new word> starts conversation were will ask you input english and ukraine word, "
        "after what save it to your dictionary.\n\n"
        "Each day bot will increase value of words and reset it when you will repeat this words by "
        "<Repeat words> or <Get poll>\n\n"
        "<Repeat words> give you 5 pairs with highest value\n\n"
        "<Get poll> propose you poll with ukraine or english words to translate",
        reply_markup=ReplyKeyboardMarkup(buttons_start, resize_keyboard=True),
    )


# set up one new word hands on
ENGLISH, UKRAINE = range(2)


async def set_up_new_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start of new conversation to set up new eng/uk pair"""
    await update.message.reply_text("Hi, send me english word, that you want to save")
    return ENGLISH


async def english(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.message.text
    context.user_data["english"] = query
    await update.message.reply_text(
        "Okey, what is this word meaning in ukraine?",
    )

    return UKRAINE


async def ukraine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End of conversation"""
    query = update.message.text
    context.user_data["ukraine"] = query
    data = (
        context.user_data["english"],
        context.user_data["ukraine"],
        update.message.from_user.id,
    )
    await add_new_pair(data)
    await update.message.reply_text(
        "Ok, i will set up this pair into your dictionary",
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Okay, lets go to main menu.", reply_markup=ReplyKeyboardMarkup(buttons_start)
    )

    return ConversationHandler.END


# get 10 new random words
async def choose_speech_part(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Hye, it's time to lear some new words. Please choose what part of speech you want learn today.",
        reply_markup=ReplyKeyboardMarkup(buttons_speech_parts),
    )


async def remind_lately(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Put off event with learning new words on 15 minute"""
    context.job_queue.run_once(choose_speech_part, time(0, 15))
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Okay, I will remind you in 15 minutes.",
        reply_markup=ReplyKeyboardMarkup(buttons_start, resize_keyboard=True),
    )


async def speech_part_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send to chat 10 words from selected speech part"""
    if update.message.text == commands[-1]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Okay, lets go to main menu.",
            reply_markup=ReplyKeyboardMarkup(buttons_start, resize_keyboard=True),
        )

    text = await google_translate(update.message.text, update.message.from_user.id)
    if len(text) < 10:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=ReplyKeyboardMarkup(buttons_start, resize_keyboard=True),
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Seems you reached the end of this speech part in my library.",
            reply_markup=ReplyKeyboardMarkup(buttons_start, resize_keyboard=True),
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=ReplyKeyboardMarkup(buttons_start, resize_keyboard=True),
        )


# set_up daily events conversation
MORNING, EVENING, END = range(3)


async def set_up_time_learn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start of conversation to set up time for all daily events"""
    await update.message.reply_text(
        "Hi, write time, when you want learn new words in <hh:mm> format"
    )
    return MORNING


async def set_up_time_morning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.message.text
    context.user_data["learn"] = datetime.strptime(query, "%H:%M").time()
    await update.message.reply_text(
        "Now, write time, when you want repeat words in the morning in <hh:mm> format",
    )
    return EVENING


async def set_up_time_evening(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.message.text
    context.user_data["morning"] = datetime.strptime(query, "%H:%M").time()
    await update.message.reply_text(
        "Now, write time, when you want repeat words in the evening in <hh:mm> format",
    )
    return END


async def set_up_time_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """End of conversation to set up time for all daily events"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    query = update.message.text
    context.user_data["evening"] = datetime.strptime(query, "%H:%M").time()
    context.job_queue.run_once(run_daily, 1, chat_id=chat_id, user_id=user_id)
    await update.message.reply_text(
        f"Greate, I will set up this time for you\n We will learn new words at {context.user_data['learn']}.\n "
        f"And I will remind its to you at {context.user_data['morning']} and {context.user_data['evening']} ",
    )
    return ConversationHandler.END


async def run_daily(context: ContextTypes.DEFAULT_TYPE):
    """Delete old jobs at run new, after user's change settings"""
    chat_id = context.job.chat_id
    user_id = context.job.user_id
    await remove_job_if_exists("morning", context)
    await remove_job_if_exists("learn", context)
    await remove_job_if_exists("evening", context)
    await remove_job_if_exists("increase", context)
    context.job_queue.run_daily(
        remind_newest_words_event,
        time=context.user_data["morning"],
        chat_id=chat_id,
        data=user_id,
        name="morning",
    )
    context.job_queue.run_daily(
        choose_speech_part,
        time=context.user_data["learn"],
        chat_id=chat_id,
        data=user_id,
        name="learn",
    )
    context.job_queue.run_daily(
        remind_newest_words_event,
        time=context.user_data["evening"],
        chat_id=chat_id,
        data=user_id,
        name="evening",
    )
    context.job_queue.run_daily(
        increase_rating,
        time=time(0, 1, 0, tzinfo=pytz.timezone("Europe/Kyiv")),
        chat_id=chat_id,
        data=user_id,
        name="increase",
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"{context.user_data['morning']}, {context.user_data['learn']}, {context.user_data['evening']}",
    )


async def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE):
    """Remove job with given name"""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    for job in current_jobs:
        job.schedule_removal()


async def remind_newest_words_event(context: ContextTypes.DEFAULT_TYPE):
    """Send 10 newest pairs, only for daily event"""
    job = context.job
    text = await newest_words((job.data,))
    await context.bot.send_message(chat_id=job.chat_id, text=text)


async def remind_highest_rating_words(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Send 5 highest rating pairs, hands on"""
    user_id = update.message.from_user.id
    max_rating = await get_rating((user_id,))
    all_pairs = await words_with_highest_rating((user_id, max_rating))
    pairs = random.sample(all_pairs, k=5)
    reset = [(pair[0], pair[1], user_id) for pair in pairs]
    text = "\n".join([f"{word[0]} - {word[1]}" for word in pairs])
    await update.message.reply_text(text)
    for pair in reset:
        await reset_rating(pair)


# Poll branch
async def choose_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Please choose, you want poll with UK or ENG word?",
        reply_markup=ReplyKeyboardMarkup(buttons_poll, resize_keyboard=True),
    )


async def translate_from_uk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    eng_words = await get_all_eng_words((user_id,))
    data = (user_id, await get_rating((user_id,)))
    pairs = await words_with_highest_rating(data)
    pair = random.choice(pairs)
    eng_word = pair[0]
    ua_word = pair[1]
    eng_words.remove(eng_word)
    words_for_test = random.sample(eng_words, k=4)
    words_for_test.append(eng_word)
    random.shuffle(words_for_test)
    correct = words_for_test.index(eng_word)

    question = f"Translate this word: {ua_word}"
    context.job_queue.run_once(reset_rating, 1, data=(eng_word, ua_word, user_id))
    await context.bot.send_poll(
        chat_id=update.message.chat_id,
        question=question,
        options=words_for_test,
        type=Poll.QUIZ,
        correct_option_id=correct,
    )


async def translate_from_eng(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    ua_words = await get_all_ua_words(user_id)
    data = (user_id, await get_rating((user_id,)))
    pairs = await words_with_highest_rating(data)
    pair = random.choice(pairs)
    eng_word = pair[0]
    ua_word = pair[1]
    ua_words.remove(ua_word)
    words_for_test = random.sample(ua_words, k=4)
    words_for_test.append(ua_word)
    random.shuffle(words_for_test)
    correct = words_for_test.index(ua_word)

    question = f"Translate this word: {eng_word}"
    context.job_queue.run_once(reset_rating, 1, data=(eng_word, ua_word, user_id))
    await context.bot.send_poll(
        chat_id=update.message.chat_id,
        question=question,
        options=words_for_test,
        type=Poll.QUIZ,
        correct_option_id=correct,
    )
