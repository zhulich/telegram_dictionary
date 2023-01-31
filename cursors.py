from telegram.ext import ContextTypes

from config import (
    cnx,
    SELECT_UA,
    MAX_RATING,
    RATING_INCREASE,
    RATING_ZERO,
    SELECT,
    INSERT,
    SELECT_NEWEST,
    SELECT_ENG,
)


async def get_all_ua_words(user_id):
    cursor = cnx.cursor()
    cursor.execute(SELECT_UA, (user_id,))
    ua_words = cursor.fetchall()
    return [word[0] for word in ua_words]


async def get_all_eng_words(user_id):
    cursor = cnx.cursor()
    cursor.execute(SELECT_ENG, user_id)
    eng_words = cursor.fetchall()
    return [word[0] for word in eng_words]


async def get_rating(data):
    cursor = cnx.cursor()
    cursor.execute(MAX_RATING, data)
    rating = cursor.fetchall()
    cursor.close()
    return rating[0][0]


async def increase_rating():
    cursor = cnx.cursor()
    cursor.execute(RATING_INCREASE)
    cnx.commit()
    cursor.close()


async def reset_rating_job(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    cursor = cnx.cursor()
    cursor.execute(RATING_ZERO, data)
    cnx.commit()
    cursor.close()


async def reset_rating(data):
    cursor = cnx.cursor()
    cursor.execute(RATING_ZERO, data)
    cnx.commit()
    cursor.close()


async def words_with_highest_rating(data):
    cursor = cnx.cursor()
    cursor.execute(SELECT, data)
    pairs = cursor.fetchall()
    cursor.close()
    return pairs


async def newest_words(data):
    cursor = cnx.cursor()
    cursor.execute(SELECT_NEWEST, data)
    pairs = cursor.fetchall()
    text = "\n".join([f"{word[0]} - {word[1]}" for word in pairs])
    cursor.close()
    return text


async def add_new_pair(data):
    cursor = cnx.cursor()
    cursor.execute(INSERT, data)
    cnx.commit()
    cursor.close()
