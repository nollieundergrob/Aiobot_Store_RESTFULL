
from django.db import models
import datetime

class LoginForm(models.Model):
    username = models.CharField(max_length=100)
    telegramid = models.IntegerField('telegram_id')
    date_registration = models.CharField(default=str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M")),max_length=100)
    firstname = models.CharField(blank=True,max_length=200)
    def __str__(self):
        return self.username


class FavoriteTags(models.Model):
    user = models.ForeignKey(LoginForm,on_delete=models.CASCADE,related_name='tags')
    tag = models.CharField(max_length=100)
    def __str__(self):
        return f'{self.tag} {self.user.username}'
    
class ProductModel(models.Model):
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=700)
    price = models.IntegerField()
    date = models.CharField(verbose_name='Дата',default=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),max_length=100)
    def __str__(self):
        return self.title

class ProductPhotoModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE,related_name='photos')
    image = models.ImageField(upload_to=('images/'))
    def __str__(self):
        return f"{self.product.title}"

class ProductTagsModell(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE,related_name='tags')
    tag = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.product.title}"

class ProductProgress(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='progress')
    user = models.ForeignKey(LoginForm, on_delete=models.CASCADE, related_name='product_progress')  # Changed 'id' to 'product_progress'

    def __str__(self):
        return f"{self.product.title} - {self.user.username}"
