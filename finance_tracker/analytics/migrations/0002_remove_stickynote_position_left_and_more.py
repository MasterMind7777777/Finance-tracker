# Generated by Django 4.2.1 on 2023-05-26 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stickynote',
            name='position_left',
        ),
        migrations.RemoveField(
            model_name='stickynote',
            name='position_top',
        ),
    ]
