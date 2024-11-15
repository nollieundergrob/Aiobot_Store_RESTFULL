# Generated by Django 5.1.3 on 2024-11-06 19:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_loginform_date_registration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginform',
            name='date_registration',
            field=models.CharField(default='06.11.2024 22:27', max_length=100),
        ),
        migrations.AlterField(
            model_name='loginform',
            name='telegramid',
            field=models.IntegerField(verbose_name='telegram_id'),
        ),
        migrations.AlterField(
            model_name='productmodel',
            name='date',
            field=models.CharField(default='06.11.2024 22:27', max_length=100, verbose_name='Дата'),
        ),
        migrations.CreateModel(
            name='FavoriteTags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='USER', to='store.loginform')),
            ],
        ),
        migrations.CreateModel(
            name='ProductProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='store.productmodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_progress', to='store.loginform')),
            ],
        ),
    ]
