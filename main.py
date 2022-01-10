"""
Simple echo Telegram Bot example on Aiogram framework using
Yandex.Cloud functions.
"""

import json
import os
from random import randint

from aiogram import Bot, Dispatcher, types

import db
import similar_str


async def on_start_command(message: types.Message):
    await message.reply('Hello, {}! Please, write mem description to get an image'.format(message.from_user.first_name))


async def on_help_command(message: types.Message):
    await message.reply('Write mem description to get an image\n/help to get this message.')


async def on_rating_command(message: types.Message):
    rating_str = message.text.replace("/rating", "").replace(" ", "")
    try:
        rating = int(rating_str)
        if rating < 1 or rating > 5:
            raise ValueError

        is_success = db.save_rating(message.from_user.username, rating)
        reply = "Thank you!" if is_success else "Something went wrong, but thank you"
        await message.reply(reply)
    except ValueError:
        await message.reply("Invalid integer from 1 to 5 after /rating.")


async def on_user_texted(message: types.Message):
    # try:
    request_id = db.save_request(message.text, message.from_user.username)
    images = db.get_all_images()
    result = similar_str.find_most_similar(message.text, images)
    db.save_result(request_id, result)

    dirname = db.get_local_image_path(result.service_id)
    random = randint(1, 100)
    full_path = os.environ.get('IMAGE_PATH') + dirname + result.filename + ".gif?random={}".format(random)

    await message.answer_video(full_path)
    await message.answer(result.description)


# except Exception as e:
# raise e
# await message.answer("Something went wrong. {}".format(str(e)))


# Functions for Yandex.Cloud
async def register_handlers(dp: Dispatcher):
    """Registration all handlers before processing update."""

    dp.register_message_handler(on_start_command, commands=['start'])
    dp.register_message_handler(on_help_command, commands=['help'])
    dp.register_message_handler(on_rating_command, commands=['rating'])

    dp.register_message_handler(on_user_texted)


async def process_event(event, dp: Dispatcher):
    """
    Converting an Yandex.Cloud functions event to an update and
    handling tha update.
    """

    update = json.loads(event['body'])

    Bot.set_current(dp.bot)
    update = types.Update.to_object(update)
    await dp.process_update(update)


async def handler(event, context):
    """Yandex.Cloud functions handler."""

    if event['httpMethod'] == 'POST':
        # Bot and dispatcher initialization
        bot = Bot(os.environ.get('BOT_TOKEN'))
        dp = Dispatcher(bot)

        await register_handlers(dp)
        await process_event(event, dp)

        return {'statusCode': 200, 'body': 'ok'}
    return {'statusCode': 405}
