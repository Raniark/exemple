# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.

"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import sys, logging, requests

bot_token = sys.argv[1]  # Le premier paramètre (0) étant le nom du script (fichier)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
name = 'main'
logger = logging.getLogger(name)

START, SORTIR_CHOIX, RESTAURANTS_CHOIX, RESTO_RESULTATS, CARTES, RETOUR, TRANSPORT = range(7)


def start(bot, update):
    reply_keyboard = [['Restaurants', 'Sorties']]

    update.message.reply_text(
        'Hi! My name is Professor Bot. Je suis là pour vous aider à passer une bonne soirée en vous aidant à choisir une activité à faire.\n\n'
        'Que souhaitez-vous faire ce soir ? Plutôt un restaurant ou une sortie ?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return START


def sortir_choix(bot, update):
    reply_keyboard = [['Musées', 'Bars', 'Clubs', 'Restaurants', 'Retour']]

    user = update.message.from_user
    logger.info("Volontée de %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Parfait. Donc ce soir vous préférez vous faire une petite sortie, '
        'Voici donc les choix que je vous propose pour ce soir. ',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SORTIR_CHOIX


def musees(bot, update):
    reply_keyboard = [['Retour']]

    update.message.reply_text(
        'Vous souhaitez aller au musée peut-être?.\n'
        'Voici le top 3 des musées :\n\nMusée d\'ethnographie de Genève\nFondation Baur Musée des arts d\'Extrême-Orient\nMuséum d\'histoire naturelle de Genève',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return RETOUR


def bars(bot, update):
    reply_keyboard = [['Retour']]

    update.message.reply_text(
        'Vous voulez sortir boire un verre ?.\n\n'
        'Je vous conseille ces 3 bars :\n\nMr. Pickwick Pub Genève\n\t\tRue de Lausanne 80, 1202\n\nBritannia Pub\n\t\tPlace de Cornavin 6, 1201\n\nrooftop°42\n\t\tRue du Rhône 42',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return RETOUR


def clubs(bot, update):
    reply_keyboard = [['Retour']]

    update.message.reply_text(
        'Je connais les meilleurs clubs de Genève.\n'
        'Voici mes propositions :\n\nL\'Le Baroque\nLe Moulin Rouge Club\nJava Club',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return RETOUR


def restaurant_choix(bot, update):
    reply_keyboard = [['Italien', 'Steakhouse', 'Mexicain', 'Espagnol', 'Thaï', 'Retour']]

    user = update.message.from_user
    logger.info("%s a choisis %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Vous voulez manger un bon petit plat, '
        'Voilà donc les choix que je vous propose pour ce soir. ',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return RESTAURANTS_CHOIX


def asiate(bot, update):
    reply_keyboard = [['Restaurant1', 'Restaurant2', 'Restaurant3', 'Restaurant4', 'Restaurant5', 'Retour']]

    update.message.reply_text(
        'Voici les restaurants actuellement disponible.\n\n'
        'Quelle carte souhaiez-vous lire ?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return RESTO_RESULTATS


def resto1(bot, update):
    reply_keyboard = [['Autres restaurants']]
    update.message.reply_location(48.862725, 2.287592)
    update.message.reply_text(
        'Hi! My name is Professor Bot. Je suis là pour vous aider à passer une bonne soirée en vous aidant à choisir une activité à faire.\n\n'
        'Que souhaitez-vous faire ce soir ? Plutôt un restaurant ou une sortie ?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CARTES


def appeler_opendata(path):
    url = "http://transport.opendata.ch/v1/" + path
    print(url)
    reponse = requests.get(url)
    return reponse.json()


def afficher_arrets(update, arrets):
    texte_de_reponse = "Voici les arrets:\n"

    for station in arrets["stations"]:
        if station["id"] is not None:
            texte_de_reponse += "\n Arret: " + station["name"]

    update.message.reply_text(texte_de_reponse)


def bienvenue(bot, update):
    update.message.reply_text("Ou êtes-vous ?",
                              reply_markup=ReplyKeyboardRemove())
    return TRANSPORT


def lieu_a_chercher(bot, update):
    resultats_opendata = appeler_opendata("locations?query=" + update.message.text)
    afficher_arrets(update, resultats_opendata)
    return TRANSPORT


def coordonnees_a_traiter(bot, update):
    location = update.message.location
    resultats_opendata = appeler_opendata("locations?x={}&y={}".format(location.latitude, location.longitude))
    afficher_arrets(update, resultats_opendata)
    return TRANSPORT


def details_arret(bot, update):
    update.message.reply_text("Details concernant un arrêt")
    return TRANSPORT


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO

    conv_handler_discussion = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            START:
                [
                    RegexHandler('^(Sorties)$', sortir_choix),
                    RegexHandler('^(Restaurants)$', restaurant_choix)
                ],

            SORTIR_CHOIX:
                [
                    RegexHandler('^(Musées)$', musees),
                    RegexHandler('^(Bars)$', bars),
                    RegexHandler('^(Clubs)$', clubs),
                    RegexHandler('^(Restaurants)$', restaurant_choix),
                    RegexHandler('^(Retour)$', start)
                ],
            RETOUR:
                [
                    RegexHandler('^(Retour)$', sortir_choix)
                ],

            RESTAURANTS_CHOIX:
                [
                    RegexHandler('^(Italien)$', asiate),
                    RegexHandler('^(Steakhouse)$', asiate),
                    RegexHandler('^(Mexicain)$', asiate),
                    RegexHandler('^(Espagnol)$', asiate),
                    RegexHandler('^(Thaï)$', asiate),
                    RegexHandler('^(Retour)$', start)
                ],

            RESTO_RESULTATS:
                [
                    RegexHandler('^(Restaurant1)$', resto1),
                    RegexHandler('^(Restaurant2)$', resto1),
                    RegexHandler('^(Restaurant3)$', resto1),
                    RegexHandler('^(Restaurant4)$', resto1),
                    RegexHandler('^(Restaurant5)$', resto1),
                    RegexHandler('^(Retour)$', restaurant_choix)
                ],

            CARTES:
                [
                    RegexHandler('^(Autres restaurants)$', asiate),
                ],

        },

        fallbacks=[CommandHandler('cancel', cancel)]

    )

    conv_handler_transport = ConversationHandler(
        entry_points=[CommandHandler('transport', bienvenue)],

        states={
            TRANSPORT:
                [
                    (MessageHandler(Filters.text, lieu_a_chercher)),
                    (MessageHandler(Filters.location, coordonnees_a_traiter)),
                    (CommandHandler('detail', details_arret))
                ],

        },

        fallbacks=[CommandHandler('cancel', cancel)]

    )

    dp.add_handler(conv_handler_discussion)
    dp.add_handler(conv_handler_transport)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if name == 'main':
    main()

