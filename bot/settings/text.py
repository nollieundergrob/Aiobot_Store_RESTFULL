import requests
import json
import aiohttp
import asyncio

def get_register_text(message):
    return f'Добро пожаловать, <b>{message.from_user.first_name}</b>, в наш секонд хенд! 🌟 Здесь вы найдете не просто одежду, а настоящие архивные вещи и крутые находки, которые добавят изюминку в ваш стиль. Мы собрали для вас уникальные предметы, которые расскажут свою историю и помогут вам выделиться из толпы. Загляните к нам, и вы обязательно найдете что-то особенное! 🛍️✨'

async def welcome_text(sender_name):
    await f"Йоу,{sender_name}. мы - секонд. тут ты найдешь вещи себе по вкусу!"


async def combine_post(GET_POST):
    url = GET_POST  # Убедитесь, что URL корректный
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Content-Type": "application/json"}) as response:
            # Выводим статус-код и текст ответа для отладки
            print(f"Статус-код: {response.status}")
            try:
                result = await response.json()  # Асинхронно получаем JSON-данные
                
                # print(result)
                return result  # Возвращаем результат, если это необходимо
            except aiohttp.ContentTypeError:
                # print("Ошибка: ответ не является JSON.")
                return None

async def main():
    await combine_post(GET_POST='http://localhost:8000/product/data/get')  # Вызываем корутину combine_post

if __name__ == "__main__":
    asyncio.run(main()) 
    
    