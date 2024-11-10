from rest_framework import serializers
from .models import LoginForm,ProductModel,FavoriteTags
from rest_framework import serializers
from .models import ProductModel, ProductPhotoModel, ProductTagsModell




class FavoriteTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteTags
        fields = ['user', 'tag']

class ProductPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhotoModel
        fields = ['image']  # Укажите, какие поля вы хотите вернуть

class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTagsModell
        fields = ['tag']  # Укажите, какие поля вы хотите вернуть

class ProductSerializer(serializers.ModelSerializer):
    photos = ProductPhotoSerializer(many=True, read_only=True)  # Используем related_name 'photos'
    tags = ProductTagSerializer(many=True, read_only=True)  # Используем related_name 'tags'

    class Meta:
        model = ProductModel
        fields = ['id','title', 'description', 'price', 'photos', 'tags']  # Теперь здесь не нужно указывать source

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginForm
        tags = FavoriteTagsSerializer(many=True, read_only=True)
        fields = ('id','username', 'telegramid', 'date_registration','firstname')
