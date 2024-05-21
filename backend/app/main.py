
from fastapi import FastAPI

from app.api import api_router


app = FastAPI(
    title="backend",
    description="Backend Hr Portal",
    version="0.1.0",
    swagger_ui_parameters={"tagsSorter": "alpha"},
)

app.include_router(api_router)
# bot = telebot.TeleBot('')
#
#
# @bot.message_handler(commands=['start', 'hello'])
# def send_welcome(message):
#     user_id = message.from_user.id
#     username = message.from_user.username
#     bot.reply_to(message, user_id)
#
#
# @bot.message_handler(func=lambda msg: True)
# def echo_all(message):
#     user_id = message.from_user.id
#     username = message.from_user.username
#     bot.reply_to(message, f"{message}{user_id}{username}")


# app.add_api_route("/oidc_callback", oidc_callback)
# app.auth = Auth()

