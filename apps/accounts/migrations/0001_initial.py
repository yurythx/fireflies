# Generated by Django 5.2.2 on 2025-06-06 12:52

import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(error_messages={'unique': 'Já existe um usuário com este email.'}, max_length=254, unique=True, verbose_name='endereço de email')),
                ('is_verified', models.BooleanField(default=False, help_text='Designa se o usuário verificou o email.', verbose_name='verificado')),
                ('slug', models.SlugField(blank=True, help_text='Identificador único para URLs amigáveis', max_length=100, unique=True, verbose_name='slug')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'usuário',
                'verbose_name_plural': 'usuários',
                'ordering': ['-date_joined'],
            },
        ),
        migrations.CreateModel(
            name='VerificationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Código de 6 dígitos para verificação', max_length=6, verbose_name='código')),
                ('code_type', models.CharField(choices=[('registration', 'Registro de Conta'), ('password_reset', 'Redefinição de Senha'), ('email_change', 'Alteração de Email')], help_text='Tipo de verificação que o código será usado', max_length=20, verbose_name='tipo de código')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('expires_at', models.DateTimeField(help_text='Data e hora em que o código expira', verbose_name='expira em')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_codes', to=settings.AUTH_USER_MODEL, verbose_name='usuário')),
            ],
            options={
                'verbose_name': 'código de verificação',
                'verbose_name_plural': 'códigos de verificação',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'code_type')},
            },
        ),
    ]
