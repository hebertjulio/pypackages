# Generated by Django 3.0.4 on 2020-04-12 18:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0011_auto_20200412_1752'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='repository_name',
        ),
        migrations.RemoveField(
            model_name='package',
            name='repository_owner',
        ),
    ]