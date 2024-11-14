import aiohttp
import asyncio
import json
import datetime
import random
import socket

class TelegramUser:
    def __init__(self, username, id, date, firstname):
        self.username = username
        self.id = id
        self.date = date
        self.firstname = firstname

    async def __call__(self, session, url=socket.gethostbyname(socket.gethostname())):
        if self.username is None:
            self.username = 'NoneObject'
        payload = {
            "username": self.username,
            "telegramid": self.id,
            "date_registration": self.date,
            "firstname": self.firstname
        }
        async with session.post(url + "/telegram/users/", json=payload) as response:
            response_data = await response.json()
            print(response_data)

    def __repr__(self) -> str:
        return self.id


class Database:
    def __init__(self, db_path='localhost:8000'):
        self.base_link = "http://" + db_path
        self.product_link = self.base_link + '/product/data/'
        self.telegram_link = self.base_link + '/telegram/data/'
        self.active_list = []
        self.queue = {}
        self.last_version = True
        print(f'The database is running - {self.base_link}')

    async def check_user(self, message):
        async with aiohttp.ClientSession() as session:
            user_link = self.telegram_link + f'?userid={message.from_user.id}'
            if message.from_user.id not in self.active_list:
                async with session.get(user_link) as response:
                    get_user = await response.json()
                    if len(self.active_list) > 501:
                        self.active_list.pop(0)
                    self.active_list.append(message.from_user.id)
                    if not get_user:
                        tg = TelegramUser(
                            message.from_user.username,
                            message.from_user.id,
                            str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M")),
                            message.from_user.first_name
                        )
                        await tg(session, self.base_link)
                        print(f'Добавлен новый пользователь {message.from_user.username}')
                        return True
                    else:
                        print(f"Существующий пользователь {message.from_user.username}")
                        return False
            else:
                print(f"Существующий пользователь! {message.from_user.username}")
                return False

    async def get_photos(self, message, PackClass):
        id = message.caption.split('\n')[-1]
        async with aiohttp.ClientSession() as session:
            async with session.get(self.product_link + f'?id={id}') as response:
                photos = await response.json()
                return_list = [PackClass('.' + i['image'], 'rb') for i in photos[0]['photos']]
        return return_list

    async def product_getquery(self, query):
        async with aiohttp.ClientSession() as session:
            get_query = self.product_link + "?" + query
            async with session.get(get_query) as response:
                data = await response.json()
        return data[0]

    async def get_length_product(self, query='lenght=1'):
        async with aiohttp.ClientSession() as session:
            get_query = self.product_link + "?" + query
            async with session.get(get_query) as response:
                data = await response.json()
        return data

    async def like_product(self, message):
        async with aiohttp.ClientSession() as session:
            user_link = self.telegram_link + f'?userid={message.from_user.id}'
            async with session.get(user_link) as response:
                get_id = await response.json()
            id = get_id[0]['id']
            product_id = message.message.caption.split('\n')[-1]
            async with session.get(self.product_link + f'?id={product_id}') as response:
                tags = await response.json()
            for tag in tags[0]['tags']:
                payload = {'user': id, 'tag': tag['tag']}
                await session.post(self.base_link + '/telegram/tags/', json=payload)
            # print(f'{message.from_user.username} лайкнул {message.message.caption.split("\n")[0]}')
            return True

    async def generate_list(self, id):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.product_link) as response:
                all_products = await response.json()
            async with session.get(self.base_link + f'/telegram/tags/?userid={id}') as response:
                get_tags = await response.json()

            tags = {}
            if 'detail' not in get_tags:
                for i in get_tags:
                    tag = i['tag']
                    tags[tag] = tags.get(tag, 0) + 1
            else:
                product_list = [product['id'] for product in all_products]
                random.shuffle(product_list)
                self.queue[id] = product_list
                return

            sorted_tags = dict(sorted(tags.items(), key=lambda item: item[1], reverse=True))
            tag_priority = {tag: index for index, tag in enumerate(sorted_tags.keys())}
            sorted_products = sorted(all_products, key=lambda product: 
                min(tag_priority.get(tag['tag'], float('inf')) for tag in product['tags']) if product['tags'] else float('inf')
            )
            sorted_ids = [product['id'] for product in sorted_products]
            self.queue[id] = sorted_ids

    async def next_button(self, id):
        if id not in self.queue or not self.queue[id]:
            await self.generate_list(id)
        product_id = self.queue[id].pop(0)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.product_link + f'?id={product_id}') as response:
                product = await response.json()
        return product

    async def telegramid_to_list(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.telegram_link) as response:
                data = await response.json()
        return [item['telegramid'] for item in data]


# # Пример вызова функций
# db = Database()

# # Использование асинхронных функций с asyncio
# async def main():
#     # Пример: вызов асинхронной функции в вашем коде
#     await db.check_user(message=None)  # Замените message на ваш объект message

# asyncio.run(main())
