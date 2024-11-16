
import os
import time
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
import socket
from django.views import View
from store.forms import CustomAuthenticationForm
from rest_framework import generics, viewsets
from .models import LoginForm
from rest_framework.response import Response
from .serializers import LoginSerializer,ProductSerializer,FavoriteTagsSerializer
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import *
from requests import post,get
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
import json
from aiogram.utils.media_group import MediaGroupBuilder
import datetime
import asyncio
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from PIL import Image
from django.contrib.auth.decorators import login_required
import requests
from io import BytesIO
import logging



class ProductInfoAPIView(APIView):
    def get(self, request):
        if 'id' in request.query_params:
            queryset = ProductModel.objects.filter(id=request.query_params['id'])
        elif 'lenght' in request.query_params:
            queryset = ProductModel.objects.count()
            return Response(queryset)
        else:
            queryset = ProductModel.objects.all()
        serializer_for_queryset = ProductSerializer(instance=queryset, many=True)
        return Response(serializer_for_queryset.data)


class TelegramInfoAPIView(APIView):
    def get(self, request):
        if 'userid' in  request.query_params:
            queryset = LoginForm.objects.filter(telegramid=request.query_params['userid'])
        else:
            queryset = LoginForm.objects.all()
        serializer_for_queryset = LoginSerializer(instance=queryset, many=True)
        return Response(serializer_for_queryset.data)


class FavoriteTagsCreateView(generics.CreateAPIView):
    queryset = FavoriteTags.objects.all()
    serializer_class = FavoriteTagsSerializer

    def get(self, request):
        if 'userid' in request.query_params:
            user_id = request.query_params['userid']
            if user_id:
                # Retrieve the user based on the provided username (userid)
                user = get_object_or_404(LoginForm, telegramid=user_id)
                # Filter favorite tags for this user
                queryset = FavoriteTags.objects.filter(user=user)
                serializer_for_queryset = FavoriteTagsSerializer(instance=queryset, many=True)
                return Response(serializer_for_queryset.data)

            # If no userid is provided, return all favorite tags
            queryset = FavoriteTags.objects.all()
            serializer_for_queryset = FavoriteTagsSerializer(instance=queryset, many=True)
            return Response(serializer_for_queryset.data)


class LoginFormViewSet(viewsets.ModelViewSet):
    queryset = LoginForm.objects.all()
    serializer_class = LoginSerializer

@login_required
# result = post(url='http://localhost:8000' + "", headers={"Content-Type": "application/json"}, json=json.dumps({"username": username,"telegramid": tgid,"first_name": first_name,})
def index(request):
    data = {}
    return render(request,'menu.html',context=data)



class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthenticationForm  


from django.shortcuts import render, redirect
from .models import ProductModel, ProductPhotoModel, ProductTagsModell

def add_product(request):
    if request.method == 'GET':
        data = {
            'url': request.get_host(),
            'message':''
        }
        return render(request, 'add_product.html', context=data)
    
    elif request.method == 'POST':
        # Получаем данные из формы
        title = request.POST['title']
        description = request.POST['description'].replace('\n','<br>')
        price = request.POST['price']
        tags = request.POST['tags']  # Тэги в виде строки, разделенные запятыми
        photos = request.FILES.getlist('photo')  # Получаем список загруженных файлов

        # Создаем новый продукт
        product = ProductModel(
            title=title,
            description=description,
            price=price,
            date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M")  # Установим текущую дату
        )
        product.save()  # Сохраняем продукт в базе данных

        # Обработка тегов
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]  # Разделяем тэги и удаляем лишние пробелы
            for tag in tag_list:
                ProductTagsModell.objects.create(product=product, tag=tag)  # Создаем экземпляры тегов

        # Обработка фотографий
        for photo in photos:
            ProductPhotoModel.objects.create(product=product, image=photo)  # Создаем экземпляры фотографий

        messages.success(request, f'Добавлен новый продукт {title}')
        data = {
            'url': request.get_host(),
            'message':'Товар успешно добавлен'
        }
        return render(request, 'add_product.html', context=data) 

    return render(request, 'add_product.html')  # Возврат формы, если метод не POST

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def delete_product(request):
    if request.method == 'GET':
        data = {
            'url': request.get_host(),
            'message': '',
            'products': ProductModel.objects.all()
        }
        return render(request, 'delete_product.html', context=data)

    elif request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(ProductModel, id=product_id)
        product.delete()
        data = {
            'url': request.get_host(),
            'message': 'Товар успешно удален!',
            'products': ProductModel.objects.all()
        }
        return render(request, 'delete_product.html', context=data)  # Перенаправление на ту же страницу после удаления
    

from django.views import View
from django.shortcuts import render
from bot import database
from bot.bot import get_bot_object  # Импортируйте ваш бот
from aiogram import types  # Импортируйте необходимые классы из aiogram
import asyncio
import logging
from django.http import JsonResponse
from django.shortcuts import render

class Create_advert(View):
    def get(self, request, *args, **kwargs):
        return render(request=request, template_name='telegram_preview.html',context={'msg':''})


    async def send_message_to_all(self, message, images, bot):
        db = database.Database(socket.gethostbyname(socket.gethostname())+":25565")
        peoples = await db.telegramid_to_list()  # Получаем список всех пользователей
        print(message, images)  # Исправлено: 'image' на 'images'
        for user in peoples:
            print(user)
            try:
                if images != []:
                    media_group =MediaGroupBuilder(caption=message) # Список для медиа группы
                    for image in images:

                        print('check',image)
                        # media_group.add_photo(types.InputMediaPhoto(media=types.FSInputFile(image)))
                        media_group.add_photo(types.FSInputFile(image))
                          # Добавляем в медиа группу
                            
                        # else:
                        #     logging.warning(f'Некорректный тип файла: {type(image)}')
                    # Проверяем, не пустой ли media_group
                    if media_group:
                        await bot.send_media_group(chat_id=user, media=media_group.build())
                    else:
                        logging.warning(f'media_group пуст для пользователя {user}')
                else:
                    await bot.send_message(chat_id=user, text=message)
                    print(f'Нет фотографий')
                # if message:
                #     await bot.send_message(user, message, parse_mode='HTML')
            except Exception as e:
                print(f'Ошибка при отправке сообщения пользователю {user}: {e}')
                logging.error(f'Ошибка при отправке сообщения пользователю {user}: {e}')




    @csrf_exempt
    def post(self, request):
        text_message = request.POST.get('textMessage')  # Получаем текст сообщения
        images = request.FILES.getlist('list_image')  # Получаем список загруженных изображений
        valid_images = []
        bot = get_bot_object()
        for image in images:
            temp_file_path = f'./static/temp/{image.name}'
            print(temp_file_path)  # Путь к временным файлам
            with open(temp_file_path, 'wb') as img:
                    img.write(image.read())
            # time.sleep(5)
            valid_images.append(f'{temp_file_path}')
        if text_message or valid_images:  # Проверяем, есть ли текст или изображения
            asyncio.run(self.send_message_to_all(text_message, valid_images,bot))  # Отправляем сообщения всем пользователям
            time.sleep(1)
            for image in valid_images:
                os.remove(image)
            return render(request, 'telegram_preview.html', {'msg': 'Сообщение отправлено!'})
        else:
            time.sleep(1)
            for image in valid_images:
                os.remove(image)
            return render(request, 'telegram_preview.html', {'msg': 'Сообщение не может быть пустым.'})
        