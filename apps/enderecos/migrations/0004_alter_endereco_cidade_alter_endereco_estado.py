# Generated by Django 5.2 on 2025-04-12 17:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enderecos', '0003_estado_cidade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endereco',
            name='cidade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='enderecos.cidade'),
        ),
        migrations.AlterField(
            model_name='endereco',
            name='estado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='enderecos.estado'),
        ),
    ]
