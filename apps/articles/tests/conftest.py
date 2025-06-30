import pytest
import factory
from django.contrib.auth import get_user_model
from apps.articles.models import Article, Comment
from apps.config.models import AppModuleConfiguration

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', '123456')

class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article
    title = factory.Sequence(lambda n: f'Artigo {n}')
    slug = factory.Sequence(lambda n: f'artigo-{n}')
    content = 'Conteúdo de teste'
    status = 'published'
    author = factory.SubFactory(UserFactory)

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment
    article = factory.SubFactory(ArticleFactory)
    name = factory.Sequence(lambda n: f'Comentador {n}')
    email = factory.LazyAttribute(lambda o: f'{o.name.lower().replace(" ", "")}@example.com')
    content = 'Comentário de teste'
    is_approved = True

@pytest.fixture
def user_factory():
    return UserFactory

@pytest.fixture
def article_factory():
    return ArticleFactory

@pytest.fixture
def comment_factory():
    return CommentFactory

@pytest.fixture(autouse=True)
def enable_articles_module(db):
    AppModuleConfiguration.objects.update_or_create(
        app_name='apps.articles',
        defaults={
            'display_name': 'Artigos',
            'is_enabled': True,
            'status': 'active',
            'module_type': 'feature',
        }
    ) 