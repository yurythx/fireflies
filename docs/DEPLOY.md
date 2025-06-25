# 🐝 Guia Completo de Instalação e Deploy - FireFlies CMS

---

## 📆 Requisitos do Sistema

* Ubuntu 22.04 ou superior
* Python 3.10 ou superior
* Git
* PostgreSQL
* Nginx
* (Opcional) Certbot para HTTPS

---

## 📦 1. Instalação de Dependências

### 1.1 Atualize o sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Instale pacotes principais

```bash
sudo apt install -y python3 python3-venv python3-pip python3-dev \
build-essential libpq-dev git curl nginx
```

### 1.3 Instale e configure PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
```

#### 1.3.1 Configure banco e usuário

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE fireflies;
CREATE USER fireflies_user WITH PASSWORD 'senha_segura';
ALTER ROLE fireflies_user SET client_encoding TO 'utf8';
ALTER ROLE fireflies_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE fireflies_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE fireflies TO fireflies_user;
\q
```

### 1.4 Instale e inicie o Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

---

## 🚀 2. Deploy do FireFlies CMS

### 2.1 Clone o projeto

```bash
cd /var/www
sudo git clone <repo> fireflies
cd fireflies
sudo chown -R $USER:www-data .
```

### 2.2 Crie o ambiente virtual

```bash
python3 -m venv env
source env/bin/activate
```

### 2.3 Instale as dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Configure o .env

```bash
cp .env.example .env
nano .env
```

> Exemplo de configuração:

```
DB_NAME=fireflies
DB_USER=fireflies_user
DB_PASSWORD=senha_segura
DB_HOST=localhost
```

### 2.5 Migração do banco

```bash
python manage.py migrate
```

### 2.6 Arquivos estáticos

```bash
python manage.py collectstatic
```

### 2.7 Crie superusuário

```bash
python manage.py createsuperuser
```

### 2.8 Teste localmente

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## ⚙️ 3. Configurar Gunicorn (systemd)

### 3.1 Crie o serviço

```bash
sudo nano /etc/systemd/system/fireflies.service
```

```ini
[Unit]
Description=FireFlies Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/fireflies
EnvironmentFile=/var/www/fireflies/.env
ExecStart=/var/www/fireflies/env/bin/gunicorn core.wsgi:application --bind 127.0.0.1:8001
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start fireflies
sudo systemctl enable fireflies
```

---

## 🌐 4. Configurar o Nginx

### 4.1 Crie a configuração do site

```bash
sudo nano /etc/nginx/sites-available/fireflies
```

```nginx
server {
    listen 80;
    server_name 192.168.29.113;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/fireflies/static/;
    }

    location /media/ {
        alias /var/www/fireflies/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.2 Ative e reinicie o Nginx

```bash
sudo ln -s /etc/nginx/sites-available/fireflies /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔐 5. HTTPS (Certbot)

### 5.1 Instale Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 5.2 Gere SSL

```bash
sudo certbot --nginx -d 192.168.29.113
```

### 5.3 Teste renovação automática

```bash
sudo certbot renew --dry-run
```

---

## 🛠️ 6. Backup e Restauração

### 6.1 Backup do banco

```bash
pg_dump -U fireflies_user -h localhost fireflies > fireflies_backup.sql
```

### 6.2 Backup da mídia

```bash
tar -czvf fireflies_media_backup.tar.gz /var/www/fireflies/media/
```

---

## ⚡️ 7. Atualizando o Projeto com Segurança

### 7.1 Parar o serviço antes de atualizar

```bash
sudo systemctl stop fireflies
```

### 7.2 Atualizar o código ou dependências

* Pull do repositório:

```bash
git pull origin main
```

* Atualizar pacotes:

```bash
pip install -r requirements.txt
```

* Atualizar banco (se houver migrações):

```bash
python manage.py migrate
```

* Atualizar arquivos estáticos:

```bash
python manage.py collectstatic
```

### 7.3 Reiniciar o serviço após atualização

```bash
sudo systemctl daemon-reload
sudo systemctl restart fireflies
```

---

## ✅ Pronto!

Acesse via navegador: `http://192.168.29.113` ou `https://192.168.29.113` (com SSL).

---
