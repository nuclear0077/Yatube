# Generated by Django 3.2.16 on 2022-10-12 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20220928_1917'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={
                'verbose_name': 'Группа',
                'verbose_name_plural': 'Группы',
            },
        ),
        migrations.AlterModelOptions(
            name='post',
            options={
                'ordering': ('-pub_date',),
                'verbose_name': 'Публикация',
                'verbose_name_plural': 'Публикации',
            },
        ),
    ]