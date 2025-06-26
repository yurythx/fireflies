# 🚀 Guia de Deploy para Produção - FireFlies CMS

Este guia explica como fazer o deploy do FireFlies CMS em produção, resolvendo os problemas de mídia e TinyMCE.

## 📋 Pré-requisitos

- Python 3.8+
- Django 5.2+
- Servidor web (Nginx, Apache, etc.)
- Banco de dados configurado

## 🔧 Configurações de Produção

### 1. Variáveis de Ambiente

Configure as seguintes variáveis de ambiente no seu servidor:

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=False

# Segurança
DJANGO_SECRET_KEY=sua_chave_secreta_aqui
CSRF_TRUSTED_ORIGINS=https://seudominio.com,https://www.seudominio.com

# Banco de dados (se usar PostgreSQL)
DATABASE_URL=postgresql://usuario:senha@localhost:5432/fireflies

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app

# Site
SITE_URL=https://seudominio.com
```

### 2. Executar Script de Deploy

```bash
# Dar permissão de execução
chmod +x deploy_production.sh

# Executar deploy
./deploy_production.sh
```

### 3. Configurações Manuais

#### A. Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput --clear
```

#### B. Executar Migrações

```bash
python manage.py migrate
```

#### C. Criar Superusuário (se necessário)

```bash
python manage.py createsuperuser
```

## 🌐 Configuração do Servidor Web

### Nginx (Recomendado)

Crie um arquivo de configuração do Nginx:

```nginx
server {
    listen 80;
    server_name seudominio.com www.seudominio.com;
    
    # Redirecionar para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seudominio.com www.seudominio.com;
    
    # SSL (configure seus certificados)
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Configurações de segurança SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Diretórios
    client_max_body_size 10M;
    
    # Arquivos estáticos
    location /static/ {
        alias /path/to/fireflies/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Arquivos de mídia
    location /media/ {
        alias /path/to/fireflies/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # TinyMCE
    location /tinymce/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Aplicação Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### Apache

Crie um arquivo `.htaccess` na raiz do projeto:

```apache
# Configurações de segurança
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>

# Redirecionar para HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Servir arquivos estáticos
<FilesMatch "\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$">
    ExpiresActive On
    ExpiresDefault "access plus 1 year"
    Header set Cache-Control "public, immutable"
</FilesMatch>
```

## 🐳 Docker (Opcional)

Se preferir usar Docker, crie um `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Configurar variáveis de ambiente
ENV ENVIRONMENT=production
ENV DEBUG=False

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🔍 Verificação Pós-Deploy

### 1. Testar URLs

```bash
# Testar arquivos estáticos
curl -I https://seudominio.com/static/css/main.css

# Testar arquivos de mídia
curl -I https://seudominio.com/media/articles/images/test.jpg

# Testar TinyMCE
curl -I https://seudominio.com/tinymce/
```

### 2. Verificar Logs

```bash
# Logs do Django
tail -f logs/django.log

# Logs do servidor web
tail -f /var/log/nginx/error.log
```

### 3. Health Check

```bash
# Verificar saúde do sistema
python manage.py system_health_check

# Testar endpoint de saúde
curl https://seudominio.com/health/
```

## 🛠️ Solução de Problemas

### Problema: Mídia não carrega

**Solução:**
1. Verificar se o diretório `media/` existe e tem permissões corretas
2. Verificar configuração do servidor web para servir `/media/`
3. Verificar se a view `serve_media_files` está funcionando

### Problema: TinyMCE não carrega

**Solução:**
1. Verificar se os arquivos estáticos foram coletados
2. Verificar configurações do TinyMCE em `settings.py`
3. Verificar se não há erros de JavaScript no console

### Problema: Erro 500

**Solução:**
1. Verificar logs em `logs/django.log`
2. Verificar se `DEBUG=False` está configurado
3. Verificar se todas as variáveis de ambiente estão definidas

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs em `logs/django.log`
2. Execute `python manage.py system_health_check`
3. Verifique se todas as configurações estão corretas
4. Teste em modo de desenvolvimento primeiro

## 🎯 Checklist Final

- [ ] Variáveis de ambiente configuradas
- [ ] Arquivos estáticos coletados
- [ ] Migrações executadas
- [ ] Servidor web configurado
- [ ] SSL configurado
- [ ] Logs funcionando
- [ ] Health check passando
- [ ] Mídia carregando
- [ ] TinyMCE funcionando
- [ ] Testes realizados

---

**🎉 Parabéns! Seu FireFlies CMS está em produção!** 