from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

USER_TYPE, NAME, SURNAME, EMAIL, GENDER, AGE, PHOTO, REGION = range(8)


def start(bot, update):
    update.message.reply_text('Olá')
    reply_keyboard = [['Dono', 'Passeador']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text('Dono ou passeador?', reply_markup=reply_markup)

    return USER_TYPE


def user_type(bot, update, user_data):
    text = update.message.text
    flag_type = {'Dono': 'is_owner', 'Passeador': 'is_walker'}[text]
    user_data[flag_type] = 1
    
    update.message.reply_text('Nome?')

    return NAME

def name(bot, update, user_data):
    text = update.message.text
    user_data['name'] = text

    update.message.reply_text('Sobrenome?')

    return SURNAME


def surname(bot, update, user_data):
    text = update.message.text
    user_data['surname'] = text

    update.message.reply_text('Email?')

    return EMAIL


def email(bot, update, user_data):
    text = update.message.text
    user_data['email'] = text

    update.message.reply_text('Sexo?')

    return GENDER


def gender(bot, update, user_data):
    text = update.message.text
    user_data['gender'] = text

    update.message.reply_text('Idade?')

    return AGE


def age(bot, update, user_data):
    text = update.message.text
    user_data['age'] = int(text)

    update.message.reply_text('Nos envie uma foto sua')

    return PHOTO


def photo(bot, update, user_data):
    text = update.message.text
    user_data['photo'] = img_to_url(text)

    update.message.reply_text('Regiao?')

    return REGION


def region(bot, update, user_data):
    text = update.message.text
    user_data['region'] = update.message.text

    return ConversationHandler.END


def main():
    updater = Updater('TOKEN')
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            USER_TYPE: [MessageHandler(Filters.text, user_type, user_data=True)],

            NAME: [MessageHandler(Filters.text, name, user_data=True)],

            SURNAME: [MessageHandler(Filters.text, surname, user_data=True)],

            EMAIL: [MessageHandler(Filters.text, email, user_data=True)],

            GENDER: [MessageHandler(Filters.text, gender, user_data=True)],

            AGE: [MessageHandler(Filters.text, age, user_data=True)],

            PHOTO: [MessageHandler(Filters.photo, photo, user_data=True)],

            REGION: [MessageHandler(Filters.location, region, user_data=True)],
        },

        fallbacks=[]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
