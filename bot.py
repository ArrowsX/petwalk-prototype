from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          RegexHandler, ConversationHandler)

from sqlalchemy.sql import select
from database import engine, users, dogs, tracking

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

USER_TYPE, FIRST_NAME, LAST_NAME, AGE, GENDER, PHOTO, END_REGISTRATION = range(7)


def start(bot, update, user_data):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    
    t = select([tracking]).where(tracking.c.id == user_id) 
    if not engine.execute(t).fetchone():
        engine.execute(tracking.insert().values(id=user_id, username=username))

    s = select([users]).where(users.c.id == user_id)
    user = engine.execute(s).fetchone()
    if not user:
        update.message.reply_text('Você ainda não é um usuário registrado')
        update.message.reply_text('Vamos começar com algumas perguntas')

        reply_keyboard = [['Dono', 'Passeador']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                           one_time_keyboard=True)
        update.message.reply_text('Você quer ser registrado como dono ou passeador?',
                                  reply_markup=reply_markup)
        return END_REGISTRATION

    elif user.approved:
        update.message.reply_text('Bem vindo, %s' % user.username)
        return ConversationHandler.END

    elif not user.approved:
        update.message.reply_text('Você ainda não foi aprovado %s' % username)
        return ConversationHandler.END


def first_name(bot, update, user_data):
    flag_type = {'Dono': 'is_owner', 'Passeador': 'is_walker'}
    user_data[flag_type[update.message.text]] = 1
    update.message.reply_text('Qual é o seu nome?')
    return LAST_NAME


def last_name(bot, update, user_data):
    user_data['first_name'] = update.message.text
    update.message.reply_text('Qual é o seu sobrenome?')
    return AGE


def age(bot, update, user_data):
    user_data['last_name'] = update.message.text
    update.message.reply_text('Qual é a sua idade?')
    return GENDER


def gender(bot, update, user_data):
    user_data['age'] = update.message.text
    reply_keyboard = [['Masculino', 'Feminino']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                       one_time_keyboard=True)
    update.message.reply_text('Gênero?', reply_markup=reply_markup)
    return PHOTO


def photo(bot, update, user_data):
    user_data['gender'] = update.message.text[0]
    update.message.reply_text('Pode nos enviar uma foto sua?')
    return END_REGISTRATION


def end_registration(bot, update, user_data):
    return ConversationHandler.END


def main():
    updater = Updater('344207483:AAGTWKuFIlvXVRGG45gsHsX7ISIiNwWWxHc')
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            FIRST_NAME: [RegexHandler('^(Dono|Passeador)$', first_name, pass_user_data=True)],

            LAST_NAME: [MessageHandler(Filters.text, last_name, pass_user_data=True)],

            AGE: [MessageHandler(Filters.text, age, pass_user_data=True)],

            GENDER: [RegexHandler('^[10-99]+$', gender, pass_user_data=True)],

            PHOTO: [RegexHandler('^(Masculino|Feminino)$', photo, pass_user_data=True)],

            END_REGISTRATION: [MessageHandler(Filters.photo, end_registration, pass_user_data=True)],
        },

        fallbacks=[],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
