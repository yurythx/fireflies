# Generated by Django 5.2 on 2025-04-08 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0009_delete_reply'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
