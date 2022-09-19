import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from dashboard.config import *
from utils.db import BotDB
from utils.parser import Parser

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)

db = BotDB(DB_URI)

parser = Parser(PAIRS, EXCHANGES, HEADERS, DB_URI)


@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if (not db.subscriber_exists(message.from_user.id)):
        db.add_subscriber(message.from_user.id)
    else:
        db.update_subscription(message.from_user.id, True)

    await message.answer(
        "Subscribed to updates")

@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if(not db.subscriber_exists(message.from_user.id)):
        db.add_subscriber(message.from_user.id, False)
        await message.answer("You are not subscribed")
    else:
        db.update_subscription(message.from_user.id, False)
        await message.answer("Successfully unsubscribed")


async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        top, orders = await parser.get_symbols()
        subscriptions = db.get_subscriptions()
        for s in subscriptions:
            await bot.send_message(s[0], top, parse_mode='HTML')
            if len(orders) > 4096:
                for x in range(0, len(orders), 4096):
                    await bot.send_message(s[0], orders[x:x + 4096], parse_mode='HTML')
            else:
                await bot.send_message(s[0], orders, parse_mode='HTML')


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    asyncio.create_task(scheduled(15))


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


# # запускаем лонг поллинг
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.create_task(scheduled(60))
#     executor.start_polling(dp, skip_updates=True, loop=loop)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(dispatcher=dp,
                  webhook_path=WEBHOOK_PATH,
                  skip_updates=True,
                  on_startup=on_startup,
                  on_shutdown=on_shutdown,
                  host=WEBAPP_HOST,
                  port=WEBAPP_PORT)