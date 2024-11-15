
from .views import *
from django.urls import path,include
from rest_framework.routers import DefaultRouter

# Strore viewport urls

router = DefaultRouter()
router.register(r'users',LoginFormViewSet)



urlpatterns = [
    path('', view=index, name='index'),
    path('telegram/', include(router.urls)),
    path('telegram/data/', TelegramInfoAPIView.as_view(),),
    path('product/data/',ProductInfoAPIView.as_view()),
    path('telegram/tags/', FavoriteTagsCreateView.as_view()),
    path('product/add_product',view=add_product),
    path('product/delete_product',view=delete_product),
    path('test/', view=Create_advert.as_view(), name='create_advert'),
]
    
    
