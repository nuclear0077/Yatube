# Generated by Django 2.2.16 on 2022-11-06 06:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20221102_1622'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписчик', 'verbose_name_plural': 'Подписчики'},
        ),
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='Пост к которому написан комментарий'),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Прикрепите картинку для загрузки', null=True, upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
