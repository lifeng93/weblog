# Generated by Django 2.1.7 on 2019-03-27 22:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0002_auto_20190318_1701'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='is_reprint',
        ),
        migrations.RemoveField(
            model_name='article',
            name='origin_author',
        ),
    ]
