import requests
import concurrent.futures
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from django.urls import resolve, reverse, Resolver404

class Command(BaseCommand):
    help = 'Verifica links quebrados em todos os modelos que possuem conteúdo HTML ou URLs.'

    def add_arguments(self, parser):
        parser.add_argument('--timeout', type=int, default=10, help='Timeout em segundos para cada requisição HTTP.')
        parser.add_argument('--workers', type=int, default=5, help='Número de threads para verificação paralela.')
        parser.add_argument('--check-external', action='store_true', help='Verificar também links externos.')
        parser.add_argument('--app', type=str, help='Verificar apenas um app específico (ex: articles).')

    def handle(self, *args, **options):
        self.timeout = options['timeout']
        self.workers = options['workers']
        self.check_external = options['check_external']
        self.app_label = options['app']
        self.broken_links = {}
        self.base_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8000'

        self.stdout.write(self.style.SUCCESS('Iniciando verificação de links quebrados...'))

        models_to_check = self.get_models_to_check()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = []
            for model in models_to_check:
                self.stdout.write(f"Verificando modelo: {model.__name__}")
                for instance in model.objects.all():
                    links = self.extract_links(instance)
                    for link in links:
                        futures.append(executor.submit(self.check_link, link, instance))

            for future in concurrent.futures.as_completed(futures):
                future.result() # Processa o resultado, que já atualiza self.broken_links

        self.print_report()

    def get_models_to_check(self):
        """Identifica modelos que podem conter links."""
        models = []
        app_labels = [self.app_label] if self.app_label else [app.label for app in apps.get_app_configs()]

        for app_label in app_labels:
            try:
                app_models = apps.get_app_config(app_label).get_models()
                for model in app_models:
                    # Heurística para encontrar modelos com conteúdo ou URLs
                    has_html_field = any(f.get_internal_type() in ['TextField', 'RichTextField'] for f in model._meta.fields)
                    has_url_method = hasattr(model, 'get_absolute_url')
                    if has_html_field or has_url_method:
                        models.append(model)
            except LookupError:
                self.stdout.write(self.style.WARNING(f'App "{app_label}" não encontrado.'))
        return list(set(models))

    def extract_links(self, instance):
        """Extrai links de campos de texto e do get_absolute_url."""
        links = set()
        # 1. get_absolute_url
        if hasattr(instance, 'get_absolute_url'):
            try:
                url = instance.get_absolute_url()
                if url:
                    links.add(urljoin(self.base_url, url))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Erro ao obter get_absolute_url para {instance}: {e}'))

        # 2. Campos de texto com HTML
        for field in instance._meta.fields:
            if field.get_internal_type() in ['TextField', 'RichTextField']:
                content = getattr(instance, field.name)
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    for a_tag in soup.find_all('a', href=True):
                        links.add(urljoin(self.base_url, a_tag['href']))
        return links

    def check_link(self, url, instance):
        """Verifica o status de um único link."""
        parsed_url = urlparse(url)
        is_internal = parsed_url.netloc == urlparse(self.base_url).netloc or not parsed_url.netloc

        if not is_internal and not self.check_external:
            return

        try:
            if is_internal:
                # Verifica a resolução da URL no Django
                path = parsed_url.path
                if path.startswith(settings.MEDIA_URL):
                    # Lógica para verificar arquivos de mídia, se necessário
                    pass
                elif path.startswith(settings.STATIC_URL):
                     # Lógica para verificar arquivos estáticos, se necessário
                    pass
                else:
                    resolve(path)
            else:
                # Verifica link externo com requests
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                if response.status_code >= 400:
                    self.add_broken_link(instance, url, response.status_code)

        except Resolver404:
            self.add_broken_link(instance, url, 'Não Resolvido (404)')
        except requests.RequestException as e:
            self.add_broken_link(instance, url, f'Erro de Conexão: {e.__class__.__name__}')
        except Exception as e:
            self.add_broken_link(instance, url, f'Erro Inesperado: {str(e)}')

    def add_broken_link(self, instance, url, status):
        model_name = instance._meta.verbose_name
        instance_id = instance.pk
        if model_name not in self.broken_links:
            self.broken_links[model_name] = []
        self.broken_links[model_name].append({'id': instance_id, 'url': url, 'status': status, 'instance': str(instance)})

    def print_report(self):
        """Imprime o relatório final de links quebrados."""
        if not self.broken_links:
            self.stdout.write(self.style.SUCCESS('Nenhum link quebrado encontrado!'))
            return

        self.stdout.write(self.style.ERROR('\n--- Relatório de Links Quebrados ---'))
        for model_name, links in self.broken_links.items():
            self.stdout.write(self.style.HTTP_INFO(f'\nModelo: {model_name}'))
            for link_info in links:
                self.stdout.write(
                    f"  - Instância: {link_info['instance']} (ID: {link_info['id']})\n" 
                    f"    URL: {link_info['url']}\n" 
                    f"    Status: {self.style.ERROR(str(link_info['status']))}"
                )
        self.stdout.write(self.style.ERROR('\n--- Fim do Relatório ---'))