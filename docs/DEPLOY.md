# Guia de Deploy - FireFlies CMS

## Pré-requisitos
- Ubuntu 22.04+
- Python 3.10+
- Git
- PostgreSQL (ou outro banco)
- Nginx
- (Opcional) Certbot para HTTPS

## Passo a Passo

### 1. Clone o projeto
```bash
git clone <repo>
cd fireflies
```

### 2. Crie e ative o ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
- Copie `.env.example` para `.env` e edite conforme seu ambiente.

### 5. Migre o banco de dados
```bash
python manage.py migrate
```

### 6. Colete os arquivos estáticos
```bash
python manage.py collectstatic
```

### 7. Crie o superusuário
```bash
python manage.py createsuperuser
```

### 8. Teste localmente
```bash
python manage.py runserver 0.0.0.0:8000
```

### 9. Configure o Gunicorn (serviço systemd)
Crie `/etc/systemd/system/fireflies.service`:
```
[Unit]
Description=FireFlies Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/caminho/para/fireflies
ExecStart=/caminho/para/fireflies/venv/bin/gunicorn core.wsgi:application --bind 127.0.0.1:8001

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl start fireflies
sudo systemctl enable fireflies
```

### 10. Configure o Nginx
Crie `/etc/nginx/sites-available/fireflies`:
```
server {
    listen 80;
    server_name seu.dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /caminho/para/fireflies;
    }
    location /media/ {
        root /caminho/para/fireflies;
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
```bash
sudo ln -s /etc/nginx/sites-available/fireflies /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 11. (Opcional) HTTPS com Certbot
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu.dominio.com
```

### 12. Backup e restauração
- Use `pg_dump` para backup do banco.
- Faça backup da pasta `/media/` para arquivos de usuário. 