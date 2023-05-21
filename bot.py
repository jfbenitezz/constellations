#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
"""
from constelaciones import *
import plotly.io as pio
from io import BytesIO
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import requests
import dropbox
from dropbox.files import WriteMode

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context
latest_fig = None
chosen_constelation = None
stars, star_coords = load_stars()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Bienvenido {user.mention_html()}, soy Ramiel encargado del mapa astral{chr(10)}Para acceder a la lista de comandos escribe: /help{chr(10)}Para ver el mapa sin constelaciones escribe: /chart{chr(10)}Para ver una constelacion de tu preferencia escribe: /add{chr(10)}Para ver el mapa con todas las constelaciones escribe: /all{chr(10)}Para acceder a un mapa interactivo escribe: /link{chr(10)}Solo se podra acceder con cuenta de dropbox o google")
    await update.message.reply_text(
        "Las constelaciones disponibles son:\nBoyero\nCasiopea\nCazo\nCygnet\nGeminis\nHydrav\nOsaMayor\nOsaMenor\nPor favor, escribe una constelación\n Luego escribe /add:")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Para ver el mapa sin constelaciones escribe: /chart{chr(10)}Para ver el mapa con todas las constelaciones escribe: /all{chr(10)}Para acceder a un mapa interactivo escribe: /link{chr(10)}")
    await update.message.reply_text(
        "Las constelaciones disponibles son:\nBoyero\nCasiopea\nCazo\nCygnet\nGeminis\nHydrav\nOsaMayor\nOsaMenor\nPara escoger una escribe su nombre y envia\nLuego escribe /add") 
    
async def allstars_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global latest_fig
    await update.message.reply_text("Espera un momento mientras procesamos la imagen")
    # Load chart using constellations fucntions

    fig = draw_stars(stars)
    text_list=["Boyero","Casiopea","Cazo","Cygnet","Geminis","Hydra","OsaMayor","OsaMenor"]
    for x in text_list:
        traza_const(fig,star_coords,x)
    latest_fig = fig
    # save the chart as an image in memory
    image_bytes = BytesIO()
    pio.write_image(fig, image_bytes, format='png')
    image_bytes.seek(0)

    # send the chart image to the user
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_bytes)

async def addstars_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global latest_fig
    global chosen_constelation
    # Wait for the user's reply and get the chosen constellation
    if (chosen_constelation.upper() not in ["BOYERO", "CASIOPEA", "CAZO", "CYGNET", "GEMINIS", "HYDRA", "OSAMAYOR", "OSAMENOR"]):
        await update.message.reply_text("Nombre de constelacion no reconocido")
    else:
        await update.message.reply_text("Espera un momento mientras procesamos la imagen")
        fig = draw_stars(stars)
        traza_const(fig,star_coords,chosen_constelation)
        latest_fig = fig
        # save the chart as an image in memory
        image_bytes = BytesIO()
        pio.write_image(fig, image_bytes, format='png')
        image_bytes.seek(0)

        # send the chart image to the user
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_bytes)


async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global latest_fig
    await update.message.reply_text("Espera un momento mientras procesamos la imagen")
    # Load chart using constellations fucntions
    fig = draw_stars(stars)
    latest_fig = fig
    # save the chart as an image in memory
    image_bytes = BytesIO()
    pio.write_image(fig, image_bytes, format='png')
    image_bytes.seek(0)
    # send the chart image to the user
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_bytes)

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dbx = dropbox.Dropbox("sl.BelHsjfErP6wkPBa8U4hWoT6Geo-a6a8uYDDebqqWUEKTErZxyL8Q80QEo_0p77ed7HpYSsgPelqtURww3OfOeKZhXRy-PVIiav2VZGhXlOvtlWtGZUCIb2J5oxr1CcBdHXp1EyU")
    fig_html = pio.to_html(latest_fig)
    # Save HTML to a temporary file
    with open('chart.html', 'w', encoding='utf-8') as f:
        f.write(fig_html)

    # upload the chart HTML file to Dropbox
    with open('chart.html', 'rb') as f:
        file_data = f.read()

    response = dbx.files_upload(
        file_data,
        '/Maps/chart.html',
        mode=WriteMode.overwrite,
        mute=True,
    )

    try:
        existing_link = dbx.sharing_list_shared_links("/Maps/chart.html").links[0]
        dbx.sharing_revoke_shared_link(existing_link.url)
    except (IndexError, dropbox.exceptions.ApiError):
        pass
    settings = dropbox.sharing.SharedLinkSettings(requested_visibility=dropbox.sharing.RequestedVisibility.public)
    settings.audience = dropbox.sharing.LinkAudience.public
    response = dbx.sharing_create_shared_link_with_settings(response.path_display, settings=settings)
    link = response.url

    # send the link to the user
    await update.message.reply_text("Se genero el mapa interactivo:")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=link)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chosen_constelation
    chosen_constelation = update.message.text

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6239347297:AAHOPjIX8JEKmAvQz3XSMPGIUpLvr6M6eS0").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help",help_command))
    application.add_handler(CommandHandler("chart",chart_command))
    application.add_handler(CommandHandler("add", addstars_command))
    application.add_handler(CommandHandler("all", allstars_command))
    application.add_handler(CommandHandler("link", send_link))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()