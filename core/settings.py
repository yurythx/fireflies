
import os #, environ



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Take environment variables from .env file
#environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = env('SECRET_KEY', default='S#perS3crEt_007')

SECRET_KEY = 'django-insecure-5iy^d-bu8b2yaat7j))09j8@6=8=ay%qwul^yn3qnvm2jqpkpi'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  #env('DEBUG')

# Assets Management
ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/') 

# load production server from .env
#ALLOWED_HOSTS        = ['localhost', 'localhost:85', '127.0.0.1',               env('SERVER', default='127.0.0.1') ]
#CSRF_TRUSTED_ORIGINS = ['http://localhost:85', 'http://127.0.0.1', 'https://' + env('SERVER', default='127.0.0.1') ]

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    
    # For django form styling
    'widget_tweaks',
    

    # TinyMCE
    'tinymce',

    'crispy_forms',
    'crispy_bootstrap5',
    
    
    'apps.pages',  # Enable the inner home (home)
    'apps.config',
    'apps.articles',
    'apps.clientes',
    'apps.fornecedores',
    'apps.enderecos',
   
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "pages"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "pages"  # Route defined in home/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "templates")  # ROOT dir for templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.context_processors.cfg_assets_root',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

if os.environ.get('DB_ENGINE') and os.environ.get('DB_ENGINE') == "mysql":
    DATABASES = { 
      'default': {
        'ENGINE'  : 'django.db.backends.mysql', 
        'NAME'    : os.getenv('DB_NAME'     , 'appseed_db'),
        'USER'    : os.getenv('DB_USERNAME' , 'appseed_db_usr'),
        'PASSWORD': os.getenv('DB_PASS'     , 'pass'),
        'HOST'    : os.getenv('DB_HOST'     , 'localhost'),
        'PORT'    : os.getenv('DB_PORT'     , 3306),
        }, 
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'apps/static'),
)


#############################################################
#############################################################

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'




TINYMCE_DEFAULT_CONFIG = {
    # 'width': 700,
    # 'height': 500,
    # 'cleanup_on_startup': True,
    # 'custom_undo_redo_levels': 20,
    # 'selector': 'textarea',
    # 'theme': 'modern',
    # 'plugins': '''
    #         textcolor save link image media preview codesample contextmenu
    #         table code lists fullscreen  insertdatetime  nonbreaking
    #         contextmenu directionality searchreplace wordcount visualblocks
    #         visualchars code fullscreen autolink lists  charmap print  hr
    #         anchor pagebreak
    #         ''',
    # 'toolbar1': '''
    #         fullscreen preview bold italic underline | fontselect,
    #         fontsizeselect  | forecolor backcolor | alignleft alignright |
    #         aligncenter alignjustify | indent outdent | bullist numlist table |
    #         | link image media | codesample |
    #         ''',
    # 'contextmenu': 'formats | link image',
    # 'menubar': True,
    # 'statusbar': True,

    'height': 500,
    'menubar': False,
    'plugins': [
        'advlist autolink lists link image charmap codesample print preview anchor',
        'searchreplace visualblocks code fullscreen',
        'insertdatetime media table textcolor paste code help wordcount'
    ],
    'toolbar': 'undo redo searchreplace | formatselect | ' +
    'bold italic forecolor backcolor | alignleft aligncenter alignright alignjustify |' +
    'outdent indent | bullist numlist |' +
    'removeformat | link image tinydrive codesample | fullscreen wordcount help',
    'content_style': 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }'
    }