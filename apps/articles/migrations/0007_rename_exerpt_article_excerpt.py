# Generated by Django 5.2 on 2025-04-07 23:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0006_alter_comment_article'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='exerpt',
            new_name='excerpt',
        ),
    ]
