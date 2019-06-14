#!/usr/bin/env python
# -*- coding: windows-1256 -*-

import logging
import os
import re
import cx_Oracle
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)

from Logger import Logger

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

__level__ = logging.INFO
logger = logging.getLogger(__name__)

START = range(1)
GENDER, CHOOSING, PHOTO, LOCATION, BIO, TYPING_REPLY, TYPING_CHOICE = range(7)
__LOGDIR__ = os.path.abspath("log")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def clean_array(in_list):
    regex = r"([\'\"\[\"])"
    regex2 = r"([\'\"\]\")])"
    matches = re.sub(regex, '\n', str(in_list))
    matches2 = re.sub(regex2, '\n', matches)
    v_rec_list = matches2.replace("\n", "")

    return v_rec_list


# region START
def start(update, context):
    try:
        connection = cx_Oracle.connect('pdbadmin', 'Zz123456', 'PY_PDB')
        cursor = connection.cursor()

        list_rep_key2 = []
        sql_rep_key2 = """
                SELECT BTNTEXT FROM TBLREPLYKEYBOARD WHERE MERGE = 1 AND VISIBLE = 0
                """
        cursor.execute(sql_rep_key2)
    except cx_Oracle.DatabaseError as e:
        logger.warning("CONNECT to database Not Ok")
        logger.error("Error Massage: " + str(e))
        return None

    for result in cursor.fetchall():
        list_rep_key2.append(result[0])
        # print(list)

    v_rec_list = clean_array(list_rep_key2)
    # print(v_rec_list)

    reply_keyboard_combine = v_rec_list.split(',')

    reply_keyboard_single = []
    sql_rep_key1 = """
            SELECT BTNTEXT FROM TBLREPLYKEYBOARD WHERE MERGE = 0 AND VISIBLE = 0
            """
    cursor.execute(sql_rep_key1)

    for result in cursor.fetchall():
        reply_keyboard_single.append(result)
        # print(list)

    reply_keyboard_single.append(reply_keyboard_combine)
    #
    # print(type(reply_keyboard_single))
    # print(reply_keyboard_single)

    # print(type(reply_keyboard_single))

    sql_start_msg = """
            SELECT MSG_START FROM TBLCONFIG WHERE ID = 1
            """
    cursor.execute(sql_start_msg)
    row_msg_cfg = cursor.fetchone()
    reply_keyboard = [['Boy', 'Girl', 'Other']]
    print(reply_keyboard_single)

    if row_msg_cfg is not None:
        # print(row_msg_cfg[0])
        update.message.reply_text(
            str(row_msg_cfg[0]),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_single, one_time_keyboard=True, resize_keyboard=True))
            # reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        # return GENDER
    else:
        print("nullable")

    cursor.close()
    connection.close()

    # return GENDER
# endregion START

# def start(update, context):
#     reply_keyboard = [['Boy', 'Girl', 'Other']]
#
#     print(type(reply_keyboard))
#
#     update.message.reply_text(
#         'Hi! My name is Professor Bot. I will hold a conversation with you. '
#         'Send /cancel to stop talking to me.\n\n'
#         'Are you a boy or a girl?',
#         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
#
#     return GENDER

def gender(update, context):
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('I see! Please send me a photo of yourself, '
                              'so I know what you look like, or send /skip if you don\'t want to.',
                              reply_markup=ReplyKeyboardRemove())

    return PHOTO


def photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Gorgeous! Now, send me your location please, '
                              'or send /skip if you don\'t want to.')

    return LOCATION


def skip_photo(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')

    return LOCATION


def location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    update.message.reply_text('Maybe I can visit you sometime! '
                              'At last, tell me something about yourself.')

    return BIO


def skip_location(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! '
                              'At last, tell me something about yourself.')

    return BIO


def bio(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def regular_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'Your {}? Yes, I would love to hear about that!'.format(text.lower()))

    return TYPING_REPLY

def custom_choice(update, context):
    update.message.reply_text('Alright, please send me the category first, '
                              'for example "Most impressive skill"')

    return TYPING_CHOICE

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("425486741:AAHCZTY806ugaWHjc56cfqGHvcFTwfAkpE4", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO

    start_conv_handler = ConversationHandler(entry_points=[CommandHandler('start', start)],
                                             states={
                                                 START: [CommandHandler('start', start)]
                                             },
                                             fallbacks = [CommandHandler('cancel', cancel)]
    )

    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('start', start)],
    #
    #     states={
    #         # GENDER: [MessageHandler(Filters.regex('^(�� ?� ������ ���� ��! ?| Ә� ?| �����?� ?| ������ ?| ����? �� ������??| �?�� ���� ����� ���?� �� GPS ?)$'), gender)],
    #         GENDER: [MessageHandler(Filters.text, gender)],
    #
    #         PHOTO: [MessageHandler(Filters.photo, photo),
    #                 CommandHandler('skip', skip_photo)],
    #
    #         LOCATION: [MessageHandler(Filters.location, location, pass_user_data=True),
    #                    CommandHandler('skip', skip_location)],
    #
    #         BIO: [MessageHandler(Filters.text, bio)]
    #     },
    #
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )



    dp.add_handler(start_conv_handler)



    # dp.add_handler(start_conv_handler)

    try:
        connection = cx_Oracle.connect('pdbadmin', 'Zz123456', 'PY_PDB')
        cursor = connection.cursor()

        list_rep_res2 = []
        sql_rep_res2 = """
            SELECT trim(regexp_substr(BTNTEXT, '[^,]+', 1, LEVEL)) str_2_tab, callfunc
                FROM TBLREPLYKEYBOARD
                CONNECT BY LEVEL <=
                    LENGTH(BTNTEXT) - 
                    LENGTH(REPLACE(BTNTEXT, ',', ''))
                    + 1
                """
        cursor.execute(sql_rep_res2)

        for result in cursor.fetchall():
            # list_rep_res2.append(result[0])
            dp.add_handler(MessageHandler(Filters.regex(result[0]), eval(result[1])))

        v_rec_list = clean_array(list_rep_res2)
        print(v_rec_list)

    except cx_Oracle.DatabaseError as e:
        logger.warning("CONNECT to database Not Ok")
        logger.error("Error Massage: " + str(e))

        return None

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    # updater.idle()

if __name__ == '__main__':
    os.environ["NLS_LANG"] = "AMERICAN_AMERICA.AL32UTF8"
    main()