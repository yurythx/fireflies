# Makefile para FireFlies CMS

.PHONY: help run test migrate makemigrations collectstatic createsuperuser shell deploy

help:
	@echo "Comandos disponíveis:"
	@echo "  run              - Rodar o servidor local"
	@echo "  test             - Rodar os testes"
	@echo "  migrate          - Aplicar migrações"
	@echo "  makemigrations   - Criar novas migrações"
	@echo "  collectstatic    - Coletar arquivos estáticos"
	@echo "  createsuperuser  - Criar superusuário"
	@echo "  shell            - Abrir shell do Django"
	@echo "  deploy           - Deploy completo (migrate, collectstatic, restart)"

run:
	python manage.py runserver

test:
	python manage.py test

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

collectstatic:
	python manage.py collectstatic --noinput

createsuperuser:
	python manage.py createsuperuser

shell:
	python manage.py shell

deploy: migrate collectstatic
	sudo systemctl restart fireflies
