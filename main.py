from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hlink
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from dotenv import load_dotenv
import logging
import os


from parsing import collect_data
from Database import SQLsubscriptions

load_dotenv()  # take environment variables from .env.

TOKEN = os.getenv('TOKEN')
URL_APP = os.getenv('URL_APP')

# initializing database connection
db = SQLsubscriptions()

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

logging.basicConfig(filename='logging.log', level=logging.INFO)


async def get_fresh_article(message: types.Message):
    '''Sending fresh article'''
    card = f"{hlink(res[1][0], res[1][1])}"
    db.update_last_seen(message.from_user.id, res[1][0])
    db.update_current(message.from_user.id, 1)
    await message.answer('Вы успешно подписались на рассылку!', reply_markup=ReplyKeyboardRemove())
    await message.answer(f'Самая свежая статья:\n{card}')


@dp.message_handler(lambda message: 'subscribe' == message.text.lower().lstrip('/')
                    or 'подписаться' in message.text.lower())
async def subscribe(message: types.Message):
    '''Subscribing user'''
    if not db.subscriber_exists(message.from_user.id):
        # adding the user if he is not in database
        db.add_subscriber(message.from_user.id)
        await get_fresh_article(message)
    elif not bool(db.get_subscription_status(message.from_user.id)):
        # updating subscription status if user is already in database and didn't subscribed
        db.update_subscribtion(message.from_user.id, True)
        await get_fresh_article(message)
    else:
        await message.answer('Вы уже подписаны!', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(lambda message: 'unsubscribe' == message.text.lower().lstrip('/')
                    or 'отписаться' in message.text.lower())
async def unsubscribe(message: types.Message):
    '''Unsubscribing user'''
    if (not db.subscriber_exists(message.from_user.id)):
        # adding the user if he is not in database with non active subscription
        db.add_subscriber(message.from_user.id, False)
        await message.answer('Вы не были подписаны.')
    elif db.get_subscription_status(message.from_user.id):
        # updating subscription status if user is already in database
        db.update_subscribtion(message.from_user.id, False)
        db.update_current(message.from_user.id, 1)
        await message.answer('Вы успешно отписались от рассылки!')
    else:
        await message.answer('Вы не подписаны.')


@ dp.message_handler(commands=['start'])
async def reply(message: types.Message):
    '''Start actions'''
    start_buttons = ['Подписаться на новости о хоккее']
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer_sticker('CAACAgIAAxkBAAED9ihiDp2t7LTEHtG9UnfuB8YpWhavggAC6AAD9wLID0IINLtj0w_TIwQ')
    await message.answer('Добро пожаловать! Чтобы подписаться, нажмите на кнопку ниже.', reply_markup=keyboard)


async def check_new_article(wait):
    '''Checking new articles'''
    #global res
    while True:
        await asyncio.sleep(wait)
        subscriptions = db.get_subscriptions()
        res = collect_data()
        for subscriber in subscriptions:
            if res[1][0] != subscriber[3]:
                db.update_last_seen(subscriber[1], res[1][0])
                card = f"{hlink(res[1][0], res[1][1])}"
                await bot.send_message(subscriber[1], f'Вышла новая статья!\n{card}')


@dp.message_handler(lambda message: 'read_more' == message.text.lower().lstrip('/') or 'читать' in message.text.lower())
async def read_more(message: types.Message):
    '''Navigation through articles'''
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    button_previous = InlineKeyboardButton(
        text="Более старая статья", callback_data='previous')
    button_next = InlineKeyboardButton(
        text="Более свежая статья", callback_data='next')
    button_fresh = InlineKeyboardButton(
        text="Самая свежая статья", callback_data='fresh')
    inline_keyboard.add(*[button_previous, button_next, button_fresh])
    await message.answer('Что дальше?', reply_markup=inline_keyboard)


@dp.message_handler()
async def other_messages(message: types.Message):
    start_buttons = ['Подписаться на новости о хоккее',
                     'Читать больше статей', 'Отписаться от рассылки']
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=2, one_time_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer('Выберите одну из кнопок ниже', reply_markup=keyboard)


@dp.callback_query_handler(text='previous')
async def previous_article(callback: types.CallbackQuery):
    '''Reading older articles. Up to 60 pcs'''
    current_article_number = db.get_current_article(
        callback.from_user.id)[0][0]
    if 0 <= current_article_number < 60:
        current_article_number += 1
        db.update_current(callback.from_user.id, current_article_number)
        card = f"{hlink(res[current_article_number][0], res[current_article_number][1])}"
        await callback.message.answer(card)
        await callback.answer()
    else:
        await callback.message.answer("Более старые статьи читайте на сайте.")
        await callback.answer()


@dp.callback_query_handler(text='next')
async def next_article(callback: types.CallbackQuery):
    '''Reading more recent articles regarding the current one'''
    current_article_number = db.get_current_article(
        callback.from_user.id)[0][0]
    if current_article_number > 1:
        current_article_number -= 1
        db.update_current(callback.from_user.id, current_article_number)
        card = f"{hlink(res[current_article_number][0], res[current_article_number][1])}"
        await callback.message.answer(card)
        await callback.answer()
    else:
        await callback.message.answer("На данный момет это самая свежая статья.")
        await callback.answer()


@dp.callback_query_handler(text='fresh')
async def fresh_article(callback: types.CallbackQuery):
    '''Getting freshest article'''
    card = f"{hlink(res[1][0], res[1][1])}"
    db.update_last_seen(callback.from_user.id, res[1][0])
    db.update_current(callback.from_user.id, 1)
    await callback.message.answer(card)
    await callback.answer()

if __name__ == "__main__":
    res = collect_data()
    loop = asyncio.get_event_loop()
    loop.create_task(check_new_article(14400))
    executor.start_polling(dp, skip_updates=True)
