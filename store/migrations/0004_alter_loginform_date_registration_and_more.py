# Generated by Django 5.1.3 on 2024-11-09 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_loginform_date_registration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginform',
            name='date_registration',
            field=models.CharField(default='09.11.2024 11:20', max_length=100),
        ),
        migrations.AlterField(
            model_name='productmodel',
            name='date',
            field=models.CharField(default='09.11.2024 11:20', max_length=100, verbose_name='Дата'),
        ),
    ]