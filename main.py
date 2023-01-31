from telegram.ext import (
    ApplicationBuilder,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler,
)

from config import API_TOKEN
from handler_filters import (
    time_filter,
    english_filter,
    ukraine_filter,
    speech_part_filter,
)
from tg_bot import (
    set_up_time_learn,
    EVENING,
    set_up_time_evening,
    set_up_time_end,
    set_up_time_morning,
    MORNING,
    END,
    cancel,
    set_up_new_word,
    english,
    ukraine,
    ENGLISH,
    UKRAINE,
    remind_lately,
    restart,
    choose_poll,
    remind_highest_rating_words,
    translate_from_uk,
    translate_from_eng,
    start,
    speech_part_handler,
    info,
)


def main():
    application = ApplicationBuilder().token(API_TOKEN).build()

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("Setup daily events"), callback=set_up_time_learn
                )
            ],
            states={
                MORNING: [
                    MessageHandler(filters=time_filter, callback=set_up_time_morning)
                ],
                EVENING: [
                    MessageHandler(filters=time_filter, callback=set_up_time_evening)
                ],
                END: [MessageHandler(filters=time_filter, callback=set_up_time_end)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
    )
    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("Add new word"), callback=set_up_new_word)
            ],
            states={
                ENGLISH: [MessageHandler(filters=english_filter, callback=english)],
                UKRAINE: [MessageHandler(filters=ukraine_filter, callback=ukraine)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
    )
    application.add_handler(
        MessageHandler(filters.Regex("Remind in 15 minutes"), remind_lately)
    )
    application.add_handler(MessageHandler(filters.Regex("Back to main menu"), restart))
    application.add_handler(MessageHandler(filters.Regex("Get poll"), choose_poll))
    application.add_handler(
        MessageHandler(filters.Regex("Repeat words"), remind_highest_rating_words)
    )
    application.add_handler(MessageHandler(filters.Regex("Ukraine"), translate_from_uk))
    application.add_handler(
        MessageHandler(filters.Regex("English"), translate_from_eng)
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(
        MessageHandler(filters=speech_part_filter, callback=speech_part_handler)
    )
    application.run_polling()


if __name__ == "__main__":
    main()
