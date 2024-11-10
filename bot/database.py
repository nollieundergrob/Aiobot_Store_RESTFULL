import requests
import asyncio
import json
import datetime
import urllib3
import random


class TelegramUser:
    def __init__(self,username,id,date,firstname):
        self.username = username
        self.id = id
        self.date = date
        self.firstname = firstname
        
    

    def __call__(self,url='http://localhost:8000'):
        if self.username == None:
            self.username = 'NoneObject'
        payload = {
            "username": self.username,
            "telegramid": self.id,
            "date_registration": self.date,
            "firstname": self.firstname
        }
        query = requests.post(url=url + "/telegram/users/", headers={"Content-Type": "application/json"}, json=payload)
        print(query.json())
    def __repr__(self) -> str:
        return self.id


class Database:
    
    def __init__(self, db_path='http://localhost:8000'):
        self.base_link = db_path
        self.product_link = self.base_link+'/product/data/'
        self.telegram_link = self.base_link+'/telegram/data/'
        self.active_list = []
        self.http  = urllib3.PoolManager()
        self.headers = {"Content-Type": "application/json"}
        self.queue = {}
        self.last_version = True
        
        print(f'The database is running - {self.base_link}')


    async def check_user(self,message):
        user_link = self.telegram_link+f'?userid={message.from_user.id}'
        if not message.from_user.id in self.active_list:
            get_user = requests.get(url=user_link, headers={"Content-Type": "application/json"},timeout=5)
            get_user = get_user.json()
            if len(self.active_list) > 501:
                self.active_list.pop(0)
                self.active_list = [message.from_user.id]
            else:
                self.active_list.append(message.from_user.id)
            if get_user == []:
                tg = TelegramUser(message.from_user.username,message.from_user.id,str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M")),message.from_user.first_name)
                tg(self.base_link)
                print(f'Добавлен новый пользователь {message.from_user.username}')
                return True
            else:
                print(f"Существующий пользователь {message.from_user.username}")
                return False
            
        else:
            print(f"Существующий пользователь! {message.from_user.username}")
            return False
    async def get_photos(self,message,PackClass):
        id = message.caption.split('\n')[-1]
        get_photos = self.product_link+f'?id={id}'
        photos = requests.get(url=get_photos, headers={"Content-Type": "application/json"},timeout=5).json()
        return_list = []
        for i in photos[0]['photos']:
            return_list.append(PackClass('.'+i['image'], 'rb'))
        return return_list
    def product_getquery(self, query):
        get_query = self.product_link+"?"+query
        print(get_query)
        data = requests.get(get_query, headers={"Content-Type": "application/json"},timeout=5)
        return data.json()[0]
    def get_length_product(self, query='lenght=1'):
        get_query = self.product_link+"?"+query
        data = requests.get(get_query, headers={"Content-Type": "application/json"},timeout=5)
        return data.json()
    async def like_product(self,message):
        user_link = self.telegram_link+f'?userid={message.from_user.id}'
        # get_id = requests.get(user_link, headers={"Content-Type": "application/json"},timeout=5).json()
        get_id = json.loads(self.http.request('GET', user_link, headers=self.headers).data.decode('utf-8'))
        id = get_id[0]['id']
        prduct_id = message.message.caption.split('\n')[-1]
        get_tags = self.product_link+f'?id={prduct_id}'
        tags = requests.get(url=get_tags, headers={"Content-Type": "application/json"},timeout=5).json()
        payload = ''
        for i in tags[0]['tags']:
            payload = {'user':id,'tag':i['tag']}
            post = self.http.request('POST', self.base_link+'/telegram/tags/', headers=self.headers, body=json.dumps(payload))
        # post = requests.post(url=self.base_link + "/telegram/tags/", headers={"Content-Type": "application/json"}, json=payload)
        # print(post)
        prd = message.message.caption.split("\n")[0]
        print(f'{message.from_user.username} лайкнул {prd}')
        return True
    # async def get_favorite_tags(self,message):
    #     user_link = self.telegram_link+f'?userid={message.from_user.id}'
    async def generate_list(self,id):
        all = json.loads(self.http.request('GET', self.product_link, headers=self.headers).data.decode('utf-8'))
        get_tags = json.loads(self.http.request('GET', self.base_link+f'/telegram/tags/?userid={id}', headers=self.headers).data.decode('utf-8'))
        # product_list = [i['id'] for i in all]
        tags ={}
        
        # for i in get_tags:
        #     if i['tag'] not in tags:
        #         tags[i['tag']] = 1
        #     else:
        #         tags[i['tag']] +=1
        # tags = dict(sorted(tags.items(), key=lambda item: item[1],reverse=True))
        # print(tags,all)
        if 'detail' not in get_tags:
            for i in get_tags:
                tag = i['tag']
                if tag not in tags:
                    tags[tag] = 1
                else:
                    tags[tag] += 1
        else:
            product_list = [i['id'] for i in all]
            product_list.random.shuffle()
            get_tags[id] = product_list
        # Сортируем теги по количеству
        sorted_tags = dict(sorted(tags.items(), key=lambda item: item[1], reverse=True))
        print("Sorted Tags:", sorted_tags)

        # Создаем список для сортировки продуктов по тегам
        tag_priority = {tag: index for index, tag in enumerate(sorted_tags.keys())}

        # Сортируем продукты по тегам
        sorted_products = sorted(all, key=lambda product: 
            min(tag_priority.get(tag['tag'], float('inf')) for tag in product['tags']) if product['tags'] else float('inf')
        )
        sorted_ids = [product['id'] for product in sorted_products]
        self.queue[id] = sorted_ids
    async def next_button(self,id):
            if id not in self.queue:
                await self.generate_list(id)
            elif self.queue[id] == []:
                await self.generate_list(id)
            
            product_id = self.queue[id].pop(0)
            product = json.loads(self.http.request('GET', self.product_link+f'?id={product_id}',headers=self.headers).data.decode('utf-8'))
            return product
       
    
    async def check_update(self,id):
        if not self.last_version:
            all = json.loads(self.http.request('GET', self.product_link, headers=self.headers).data.decode('utf-8'))
            product_list = [i['id'] for i in all]
            for i in self.queue[id]:
                if i not in product_list:
                    pass    




# db = Database() 
# data = db.next_button(1041676367)
# print(db.queue)
# print(data)



        
       
    
    
