
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from store.forms import CustomAuthenticationForm
from rest_framework import generics, viewsets
from .models import LoginForm
from rest_framework.response import Response
from .serializers import LoginSerializer,ProductSerializer,FavoriteTagsSerializer
from .models import *
from requests import post,get
from rest_framework.views import APIView
import json
import datetime



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


# result = post(url='http://localhost:8000' + "", headers={"Content-Type": "application/json"}, json=json.dumps({"username": username,"telegramid": tgid,"first_name": first_name,})
def index(request):
    username,tgid, first_name = 'nollieundergrob' ,1041676367, 'Bulat'
    data = LoginForm.objects.all()
    return HttpResponse(data)



class CustomLoginView(LoginView):
    template_name = 'forms/login.html'
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
from bot import bot
class Create_advert(View):
    def get(self,request):
        return render(request,'telegram_preview.html')
    def post(self,request):
        text = request.forms['textMessage']
        bot.send_advert()
