#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging
from random import randint
import requests
import crypto

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

PHOTO, PASSWORD = range(2)

def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
            'Hello {}'.format(update.message.from_user.first_name) +
            '. I am Sir Doggo 🐕.')

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'You can control me with these commands: \n\n' +
        '/giffmedoggo - returns a doggo pic')

def giffmedoggo(bot, update, args):
    if (args):
        url = 'http://dogocode.duckdns.org/encode'
        data = { 'message' : args[0] }
        response = requests.get(url, params=data)
        filename = 'image.png'
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            bot.send_document(chat_id=update.message.chat_id, document=open(filename, 'rb'))
        # update.message.reply_text(args[0]);
    else:
        num = randint(0,2)
        if num == 0:
            bot.send_photo(chat_id=update.message.chat_id, photo=open('../templates/encode_red.png', 'rb'))
        elif num == 1:
            bot.send_photo(chat_id=update.message.chat_id, photo=open('../templates/encode_blue.png', 'rb'))
        else:
            bot.send_photo(chat_id=update.message.chat_id, photo=open('../templates/encode_green.png', 'rb'))

def ihasdoggo(bot, update):
    update.message.reply_text('So... I see you have a message for me.')

    return PASSWORD

global PASSPHRASE
def password(bot, update):
    user = update.message.from_user
    PASSPHRASE = update.message.text
    # update.message.reply_text(PASSPHRASE)
    update.message.reply_text('Now, where is this doggo you\'ve been talking about?')

    return PHOTO

def photo(bot, update):
    user = update.message.from_user
    raw = update.message.document.file_id
    #raw = update.message.photo[-1].file_id
    name = raw + ".png"
    photo_file = bot.get_file(raw)
    photo_file.download(name)

    #url = 'http://dogocode.duckdns.org/decode'
    #file = {'media': open(name, 'rb')}
    #response = requests.post(url, files=file)

    response = crypto.decryption_api(crypto.load_image(name), "Shoob")
    update.message.reply_text(response)
    # bot.send_photo(chat_id=update.message.chat_id, photo=open(name, 'rb'))
    # update.message.reply_text('Decoded Message')

    return ConversationHandler.END

def invalid_photo(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('Giff me doggo or I\'ll get angry')

    return PHOTO

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye. I guess you didn\'t have it afterall')

    return ConversationHandler.END

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater('TOKEN')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("giffmedoggo", giffmedoggo, pass_args=True))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("ihasdoggo", ihasdoggo)],

        states={
            PHOTO: [MessageHandler(Filters.document, photo),
                    CommandHandler('invalid', invalid_photo)],
            PASSWORD: [MessageHandler(Filters.text, password)],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
