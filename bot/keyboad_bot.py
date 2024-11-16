from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

def main_kb(message):
    
    photobutton = InlineKeyboardButton(text="Фото", callback_data='post_photo')
    contactbutton = InlineKeyboardButton(text="Контакт", callback_data='post_contact')
    nextbutton = InlineKeyboardButton(text="Next", callback_data='next')
    like = InlineKeyboardButton(text="Лайк", callback_data='post_like')

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [photobutton, contactbutton],  # Первая строка
        [nextbutton],[like] 
                 # Вторая строка
    ])



    return keyboard

def start_kb(message):
    products = KeyboardButton(text="Товары")
    contact_button = KeyboardButton(text="📞 Контакт")  # Запрашивает контакт


    # Создаем клавиатуру с кнопками
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False,keyboard=[[products, contact_button]])

    return keyboard