import asyncio
import logging
import sys
import os
from aiogram import Bot, Router, html, types, Dispatcher
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties  # Import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot import keyboad_bot
from bot.database import Database
from bot.settings.text import get_register_text
# 7867149117:AAFD3RAoLXmcvhcOrn4gdwjFX6ehmYPASqY
TOKEN = '7867149117:AAFD3RAoLXmcvhcOrn4gdwjFX6ehmYPASqY'
router = Router()
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))  # Adjusted here

# Initialize the Database instance
db = None

def get_bot_object():
    global TOKEN
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    return bot

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if await db.check_user(message=message):
        await message.answer(get_register_text(message), reply_markup=keyboad_bot.start_kb(message))
        return None
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! 👋\nДобро пожаловать в наш телеграм-канал секонд-хэнд! Здесь вы найдете уникальные архивные и отборные вещи, которые помогут вам выделиться из толпы. 🌟 Не упустите возможность найти что-то особенное для себя!", reply_markup=keyboad_bot.start_kb(message))

@router.message()
async def echo_handler(message: Message) -> None:
    is_registered = await db.check_user(message=message)
    if is_registered:
        await message.reply(get_register_text(message))
        return None
    
    # Fetch product data
    if message.text == 'Товары':
        product = await db.next_button(message.from_user.id)
        if product:
            product = product[0]
            id = product['id']
            title = product['title']
            description = product['description'].replace('<br>', '\n')
            price = product['price']
            tags = ', '.join(tag['tag'] for tag in product['tags'])
            message_text = f"*{title}*\n\n{description}\n\nЦена: {price}₽\n\nТеги: {tags}\n{id}"
            photo = product["photos"][0]
            photo_path = '.' + photo['image']
            input_file = FSInputFile(photo_path)
            keyboad = keyboad_bot.main_kb(message)
            await bot.send_photo(message.from_user.id, photo=input_file, caption=message_text, parse_mode='Markdown', reply_markup=keyboad)
    elif message.text == '📞 Контакт':
        text=f'''
        Если у вас возникли вопросы или проблемы, пожалуйста, обращайтесь к соответствующим специалистам:
                         
        Технические вопросы @nollieundergrob отвечает на все технические вопросы, связанные с нашим сервисом. Если у вас возникла проблема с функционированием нашего сервиса или вам нужна помощь в настройке, пожалуйста, обращайтесь к @nollieundergrob.

        Вопросы и предложения @swaq11 готов ответить на все ваши вопросы и рассмотреть ваши предложения. Если у вас есть идеи по улучшению нашего сервиса или вам нужно обсудить какой-либо вопрос, пожалуйста, обращайтесь к @swaq11.

        Оформление заказов @loytue568 помогает с оформлением заказов и отвечает на вопросы, связанные с процессом заказа. Если у вас возникли вопросы о статусе вашего заказа или вам нужно помочь с оформлением, пожалуйста, обращайтесь к @loytue568.

        Надеемся, что это поможет вам быстро найти ответы на ваши вопросы и решить любые проблемы, которые у вас возникнут.'''
        await message.answer(text=text, reply_markup=keyboad_bot.start_kb(message))



@router.callback_query()
async def handle_button_click(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    message = callback_query.message
    id = message.message_id

    if callback_data == 'post_photo':
        photos = await db.get_photos(message, PackClass=FSInputFile)
        media = [InputMediaPhoto(media=i) for i in photos]
        await message.answer_media_group(media, reply_to_message_id=id)

    elif callback_data == 'next':
        product = await db.next_button(callback_query.from_user.id)
        if product:
            product = product[0]
            id = product['id']
            title = product['title']
            description = product['description'].replace('<br>', '\n')
            price = product['price']
            tags = ', '.join(tag['tag'] for tag in product['tags'])
            message_text = f"*{title}*\n\n{description}\n\nЦена: {price}₽\n\nТеги: {tags}\n{id}"
            photo = product["photos"][0]
            photo_path = '.' + photo['image']
            input_file = FSInputFile(photo_path)
            keyboad = keyboad_bot.main_kb(message)
            await bot.send_photo(callback_query.from_user.id, photo=input_file, caption=message_text, parse_mode='Markdown', reply_markup=keyboad)

    elif callback_data == 'post_like':
        like = await db.like_product(callback_query)
        await message.reply("Учтем ваш выбор", reply_to_message_id=id)
    elif callback_data == 'post_contact':
        # await send_advert('чекаю рассылку')
        await message.reply("Нажмите на кнопку ниже, чтобы связаться с нами",reply_to_message_id=id)
async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)

async def send_advert(message):
    peoples = await db.telegramid_to_list()
    for user in peoples:
        try:
            await bot.send_message(user, message, parse_mode='HTML')
        except:
            logging.info(f'{user} block the bot')

def start_bot(ip, port):
    global db
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    db = Database(f'{ip}:{port}')
    asyncio.run(main())

# Uncomment to run the bot
# if __name__ == "__main__":
#     start_bot('localhost', 8000)  # Adjust IP and port as needed

# send_advert('Чекаю рассылку...')