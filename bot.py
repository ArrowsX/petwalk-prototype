import time
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          RegexHandler, ConversationHandler)

from sqlalchemy.sql import select
from database import engine, users, dogs, tracking, walker_requests

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

USER_TYPE, FIRST_NAME, LAST_NAME, AGE, GENDER, PHOTO, END_REGISTRATION = range(7)
OWNER_MENU, REQUESTS, DOG_NAME, DOG_BREED, DOG_AGE, DOG_PHOTO = range(7, 13)
AVAILABLE_DOGS = range(13, 14)


def start(bot, update, user_data):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    user_data['id'] = user_id
    user_data['username'] = username

    tracker = engine.execute(
        select([tracking])
        .where(tracking.c.id == user_id)
    ).fetchone()
    if not tracker:
        engine.execute(tracking.insert().values(id=user_id, username=username))

    user = engine.execute(
        select([users])
        .where(users.c.id == user_id)
    ).fetchone()

    if not user:
        update.message.reply_text('Você ainda não é um usuário registrado')
        update.message.reply_text('Vamos começar com algumas perguntas')

        reply_keyboard = [['Dono', 'Passeador']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                           one_time_keyboard=True)
        update.message.reply_text('Você quer ser registrado como dono ou passeador?',
                                  reply_markup=reply_markup)
        return FIRST_NAME

    elif user.approved:
        update.message.reply_text('Bem vindo de volta, %s' % user.username)

        if user.user_type == 'dono':
            reply_keyboard = [
                ['Meus pedidos'],
                ['Meus dogs'],
                ['Registrar novo dog'],
                ['Solicitar serviço'], 
            ]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text('O que você deseja fazer hoje?', reply_markup=reply_markup)

            return OWNER_MENU

        elif user.user_type == 'passeador':
            update.message.reply_text('Vamos tentar achar alguns cachorros para você')
            user_data['i'] = 1
            reply_keyboard = [['👍', '👎']]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                               one_time_keyboard=True)
            dog = engine.execute(
                select([dogs])
                .where(dogs.c.id == user_data['i'])
            ).fetchone()

            update.message.reply_text('%s\n%s ano(s)' % (dog.name, dog.age),
                                      reply_markup=reply_markup)

            return AVAILABLE_DOGS

    elif not user.approved:
        update.message.reply_text('Você ainda não foi aprovado, %s' % username)
        return ConversationHandler.END


def first_name(bot, update, user_data):
    user_data['user_type'] = update.message.text.lower()
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
    user_data['approved'] = True
    engine.execute(users.insert().values(**user_data))

    update.message.reply_text('Obrigado pelo interesse')
    update.message.reply_text('Nossos administradores entrarão em contato '
                              'assim que você for aprovado')

    return ConversationHandler.END


def owner_menu(bot, update, user_data):
    text = update.message.text

    if text == 'Meus pedidos':
        user_data['i'] = 1
        reply_keyboard = [['👍', '👎']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                           one_time_keyboard=True)
        data = engine.execute(
            select([walker_requests])
            .where(walker_requests.c.owner_id == user_data['id'])
        ).fetchone()

        walker = engine.execute(
            select([users])
            .where(users.c.id == data['walker_id'])
        ).fetchone()

        dog = engine.execute(
            select([dogs])
            .where(dogs.c.id == data['dog_id'])
        ).fetchone()

        update.message.reply_text('Nome: %s %s\nCachorro: %s\nServiço: Passeio' % (walker.first_name, walker.last_name, dog.name),
                                  reply_markup=reply_markup)

        user_data['walker_username'] = walker.username

        return REQUESTS

    elif text == 'Meus dogs':
        s = select([dogs]).where(dogs.c.owner_id == user_data['id'])
        for dog in engine.execute(s):
            update.message.reply_text('{d[name]} {d[breed]} {d[age]}'.format(d=dog))

        reply_keyboard = [
            ['Meus pedidos', 'Meus dogs'],
            ['Registrar novo dog', 'Solicitar serviço'], 
            ['Não'],
        ]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text('Deseja fazer mais alguma coisa?', reply_markup=reply_markup)

        return OWNER_MENU

    elif text == 'Registrar novo dog':
        user_data.clear()
        user_data['owner_id'] = update.message.from_user.id

        update.message.reply_text('Qual o nome dele?')
        return DOG_NAME


def owner_requests(bot, update, user_data):
    text = update.message.text
    if text == '👎':
        try:
            s = select([walker_requests]).where(walker_requests.c.owner_id == user_data['id'])
            data = engine.execute(s).fetchall()[user_data['i']]
            user_data['i'] = user_data['i'] + 1

            walker = engine.execute(
                select([users])
                .where(users.c.id == data['walker_id'])
            ).fetchone()

            dog = engine.execute(
                select([dogs])
                .where(dogs.c.id == data['dog_id'])
            ).fetchone()

            reply_keyboard = [['👍', '👎']]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                               one_time_keyboard=True)
            update.message.reply_text('Nome: %s %s\nCachorro: %s\nServiço: Passeio' % (walker.first_name, walker.last_name, dog.name),
                                      reply_markup=reply_markup)
            user_data['walker_username'] = walker.username

            return REQUESTS

        except IndexError:
            update.message.reply_text('Não há mais pedidos')

            reply_keyboard = [
                ['Meus pedidos', 'Meus dogs'],
                ['Registrar novo dog', 'Solicitar serviço'], 
                ['Não'],
            ]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text('Deseja fazer mais alguma coisa?', reply_markup=reply_markup)

            return OWNER_MENU

    elif text == '👍':
        update.message.reply_text('Pedido recebido')
        time.sleep(1)
        update.message.reply_text('Agora só resta combinar o local de encontro com @LaisZucatto')
        time.sleep(1)
        update.message.reply_text('Obrigado')

        return ConversationHandler.END


def available_dogs(bot, update, user_data):
    text = update.message.text
    if text == '👎':
        try:
            user_data['i'] = user_data['i'] + 1
            reply_keyboard = [['👍', '👎']]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                               one_time_keyboard=True)
            dog = engine.execute(
                select([dogs])
                .where(dogs.c.id == user_data['i'])
            ).fetchone()

            update.message.reply_text('%s\n%s ano(s)' % (dog.name, dog.age),
                                      reply_markup=reply_markup)

            return AVAILABLE_DOGS

        except AttributeError:
            update.message.reply_text('Não há mais cachorros disponíveis')

            return ConversationHandler.END

    elif text == '👍':
        update.message.reply_text('Pedido recebido')
        time.sleep(1)
        update.message.reply_text('Caso você for aprovado, o dono entrará em contato com você em breve')
        update.message.reply_text('Obrigado')

        return ConversationHandler.END


def dog_name(bot, update, user_data):
    user_data['name'] = update.message.text

    update.message.reply_text('Qual a raça dele?')
    return DOG_BREED


def dog_breed(bot, update, user_data):
    user_data['breed'] = update.message.text

    update.message.reply_text('Qual a idade dele?')
    return DOG_AGE


def dog_age(bot, update, user_data):
    user_data['age'] = int(update.message.text)

    update.message.reply_text('Pode nos enviar uma foto dele?')
    return DOG_PHOTO


def dog_photo(bot, update, user_data):
    engine.execute(dogs.insert().values(**user_data))
    update.message.reply_text('Obrigado! Seu cachorro acaba de ser registrado no nosso sistema.')

    reply_keyboard = [
        ['Meus pedidos', 'Meus dogs'],
        ['Registrar novo dog', 'Solicitar serviço'], 
        ['Não'],
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text('Deseja fazer mais alguma coisa?', reply_markup=reply_markup)

    return REQUESTS


def cancel(bot, update):
    update.message.reply_text('Obrigado')

    return ConversationHandler.END


def main():
    updater = Updater('340733779:AAE8ZqxhUpDRddzoK23TdPfphWi5JEhVhFM')
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

            OWNER_MENU: [RegexHandler('^(Meus pedidos|Meus dogs|Registrar novo dog)$',
                                      owner_menu, pass_user_data=True)],

            REQUESTS: [RegexHandler('^(👍|👎)$', owner_requests, pass_user_data=True)],

            AVAILABLE_DOGS: [RegexHandler('^(👍|👎)$', available_dogs, pass_user_data=True)],

            DOG_NAME: [MessageHandler(Filters.text, dog_name, pass_user_data=True)],

            DOG_BREED: [MessageHandler(Filters.text, dog_breed, pass_user_data=True)],

            DOG_AGE: [MessageHandler(Filters.text, dog_age, pass_user_data=True)],

            DOG_PHOTO: [MessageHandler(Filters.photo, dog_photo, pass_user_data=True)],

        },

        fallbacks=[RegexHandler('^Não$', cancel)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
