import asyncio
import logging
import sys
from settings.config import *
from settings.text import *
from aiogram import Bot, Router, html, types, Dispatcher
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import FSInputFile,InputMedia,InputMediaPhoto
import keyboad_bot
from database import Database
import datetime


import os
print(os.getcwd())
router = Router()
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
db = Database()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if await db.check_user(message=message):
        await message.answer(get_register_text(message),reply_markup=keyboad_bot.start_kb(message))
        return None
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!",reply_markup=keyboad_bot.start_kb(message))


@router.message()
async def echo_handler(message: Message) -> None:
    # print(message.__dict__)
    # db.check_user(message)

    is_registered = await db.check_user(message=message)
    if is_registered:
        await message.reply(get_register_text(message))
        return None
    data =  await  combine_post('http://localhost:8000/product/data/')
    for item_data in data:
        item = item_data
        id = item['id']  
        title = item['title']
        description = item['description'].replace('<br>', '\n')
        price = item['price']
        tags = ', '.join(tag['tag'] for tag in item['tags'])
        message_text = f"*{title}*\n\n{description}\n\nЦена: {price}₽\n\nТеги: {tags}\n{id}"
        
        photo = item_data["photos"][0]
        photo_path = '.'+photo['image']
        input_file = FSInputFile(photo_path)
        keyboad = keyboad_bot.main_kb(message)
        await bot.send_photo(message.chat.id, photo=input_file, caption=message_text, parse_mode='Markdown', reply_markup=keyboad)

@router.callback_query()
async def handle_button_click(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    message = callback_query.message
    # print(callback_query)
    id = message.message_id
    if callback_data == 'post_photo':
        photos = await db.get_photos(message,PackClass=FSInputFile)  # Предполагается, что этот метод возвращает список URL или файлов
        title = message.caption.split('\n')[0]
        caption = message.caption
        
        media = [InputMediaPhoto(media=i) for i in photos]
        await message.answer_media_group(media,reply_to_message_id=id)
    elif callback_data == 'post_contact':
        await bot.send_message(callback_query.from_user.id, "Вы нажали кнопку 'Контакт'!")
    elif callback_data == 'next':
        product = db.next_button(callback_query.from_user.id)[0]
        id = product['id']  
        title = product['title']
        description = product['description'].replace('<br>', '\n')
        price = product['price']
        tags = ', '.join(tag['tag'] for tag in product['tags'])
        message_text = f"*{title}*\n\n{description}\n\nЦена: {price}₽\n\nТеги: {tags}\n{id}"
        photo = product["photos"][0]
        photo_path = '.'+photo['image']
        input_file = FSInputFile(photo_path)
        keyboad = keyboad_bot.main_kb(message)
        await bot.send_photo(callback_query.from_user.id, photo=input_file, caption=message_text, parse_mode='Markdown', reply_markup=keyboad)
        # await bot.send_message(callback_query.from_user.id, "Вы нажали кнопку 'Next'!")
    elif callback_data == 'previous':
        await bot.send_message (callback_query.from_user.id, "Вы нажали кнопку 'Previous'!")
    elif callback_data == 'post_like':
        like = await db.like_product(callback_query)
        await message.reply("Учтем ваш выбор",reply_to_message_id=id)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    dp.include_router(router)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())