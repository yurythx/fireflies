# Generated by Django 5.2.2 on 2025-06-27 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_alter_comment_website'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='image_caption',
            field=models.CharField(blank=True, help_text='Legenda opcional para a imagem destacada', max_length=255, verbose_name='legenda da imagem'),
        ),
    ]
