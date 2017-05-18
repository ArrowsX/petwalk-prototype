from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          RegexHandler, ConversationHandler)

from pony.orm import db_session, select
from database import User, Dog

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

REQUEST, CHOOSING, PENDING, WALKER = range(4)


def start(bot, update):
    reply_keyboard = [['Yes', 'No']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("Hello Donald! You didn't make any requests yet. Wanna check for available dogs?", reply_markup=reply_markup)

    return REQUEST


def request_dog(bot, update):
    text = update.message.text
    reply_keyboard = [['Yes', 'No']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    
    if text == 'Yes':
        update.message.reply_text("Good! Let's begin")
        update.message.reply_photo(open('pluto.png', 'rb'), caption='Owner: Mickey', reply_markup=reply_markup)

        return PENDING

    else:
        update.message.reply_text('Thank you!')
        return ConversationHandler.END


def pending(bot, update):
    update.message.reply_text('Ok, thank you! Once approved, the owner will contact you soon!')

    return ConversationHandler.END


def owner(bot, update):
    reply_keyboard = [['Check my requests'], ['List my dogs'], ['Add new dog']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("Hello Mickey! What do you want to do today?", reply_markup=reply_markup)

    return CHOOSING


def choice(bot, update):
    text = update.message.text
    reply_keyboard = [['Yes', 'No']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    if text == 'Check my requests':
        update.message.reply_photo(open('donald.jpg', 'rb'), caption='Donald Duck\nAge: 22\nRegion: Disney', reply_markup=reply_markup)

        return WALKER

    elif text == 'List my dogs':
        update.message.reply_text('Pluto\nBreed: Bloodhound\nAge:5')

        return ConversationHandler.END
    
    elif text == 'Add new dog':
        pass


def choose_walker(bot, update):
    text = update.message.text

    if text == 'Yes':
        update.message.reply_text('Ok, this is his username @TestYanBot. Please contact him.')
        update.message.reply_text('Please send us your route afterwards for fare calculation.')

        return ConversationHandler.END

    elif text == 'No':
        pass

def done(bot, update):
    update.message.reply_text('Thank you!')

    return ConversationHandler.END


def main():
    updater = Updater('340733779:AAE8ZqxhUpDRddzoK23TdPfphWi5JEhVhFM')
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('owner', owner)],

        states={
            REQUEST: [RegexHandler('^(Yes|No)$', request_dog)],

            CHOOSING: [RegexHandler('^(Check my requests|List my dogs|Add new dog)$', choice)],

            PENDING: [RegexHandler('^(Yes|No)$', pending)],

            WALKER: [RegexHandler('^(Yes|No)$', choose_walker)],
        },

        fallbacks=[RegexHandler('^Done$', done)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
