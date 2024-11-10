
from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.LoginForm)
admin.site.register(models.ProductModel)
admin.site.register(models.ProductPhotoModel)
admin.site.register(models.ProductTagsModell)
admin.site.register(models.FavoriteTags)
admin.site.register(models.ProductProgress)


