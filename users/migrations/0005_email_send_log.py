# Generated by Django 2.1.7 on 2019-03-03 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20190302_1310'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email_send_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=11, verbose_name='phone')),
                ('email', models.EmailField(max_length=255)),
                ('token', models.CharField(max_length=24)),
                ('send_time', models.DateTimeField(auto_now_add=True)),
                ('is_valid', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'email_send_log',
            },
        ),
    ]
