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
TOKEN = '5941816417:AAH-XBJ6ppThjKF-U5NIels_6TVfMykqbzI'
router = Router()
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))  # Adjusted here

# Initialize the Database instance
db = None

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if await db.check_user(message=message):
        await message.answer(get_register_text(message), reply_markup=keyboad_bot.start_kb(message))
        return None
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!", reply_markup=keyboad_bot.start_kb(message))

@router.message()
async def echo_handler(message: Message) -> None:
    is_registered = await db.check_user(message=message)
    if is_registered:
        await message.reply(get_register_text(message))
        return None

    # Fetch product data
    data = await db.get_length_product()  # Adjusted to call the database method
    for item_data in data:
        id = item_data['id']  
        title = item_data['title']
        description = item_data['description'].replace('<br>', '\n')
        price = item_data['price']
        tags = ', '.join(tag['tag'] for tag in item_data['tags'])
        message_text = f"*{title}*\n\n{description}\n\nЦена: {price}₽\n\nТеги: {tags}\n{id}"
        
        photo = item_data["photos"][0]
        photo_path = '.' + photo['image']
        input_file = FSInputFile(photo_path)
        keyboad = keyboad_bot.main_kb(message)
        await bot.send_photo(message.chat.id, photo=input_file, caption=message_text, parse_mode='Markdown', reply_markup=keyboad)

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

async def send_advert(token,message):
    peoples = await db.telegramid_to_list()
    for user in peoples:
        try:
            await bot.send_message(user, message, parse_mode='HTML')
        except:
            logging.info(f'USER BY ID {user} LEAVE')

def start_bot(ip, port):
    global db
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    db = Database(f'{ip}:{port}')
    asyncio.run(main())

# Uncomment to run the bot
# if __name__ == "__main__":
#     start_bot('localhost', 8000)  # Adjust IP and port as needed

# send_advert('Чекаю рассылку...')