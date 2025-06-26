# 🔧 Correção Manual em Produção - FireFlies CMS

## 📋 Comandos para Executar no Servidor

### **1. Parar o Servidor (se estiver rodando)**
```bash
# Se estiver usando systemd
sudo systemctl stop fireflies

# Se estiver usando supervisor
sudo supervisorctl stop fireflies

# Se estiver rodando manualmente
# Pressione Ctrl+C para parar
```

### **2. Navegar para o Diretório do Projeto**
```bash
cd /caminho/para/seu/projeto/fireflies
```

### **3. Ativar o Ambiente Virtual (se estiver usando)**
```bash
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows
```

### **4. Coletar Arquivos Estáticos**
```bash
python manage.py collectstatic --noinput --clear
```

### **5. Executar Migrações (se necessário)**
```bash
python manage.py migrate
```

### **6. Verificar Permissões dos Diretórios**
```bash
# Criar diretório de logs se não existir
mkdir -p logs
touch logs/django.log

# Ajustar permissões
chmod 755 media/
chmod 755 staticfiles/
chmod 644 logs/django.log

# Se estiver usando Linux/Mac, ajustar proprietário
sudo chown -R www-data:www-data media/
sudo chown -R www-data:www-data staticfiles/
sudo chown -R www-data:www-data logs/
```

### **7. Testar Configurações**
```bash
# Verificar se as configurações estão corretas
python manage.py check

# Verificar saúde do sistema
python manage.py system_health_check
```

### **8. Reiniciar o Servidor**
```bash
# Se estiver usando systemd
sudo systemctl start fireflies
sudo systemctl status fireflies

# Se estiver usando supervisor
sudo supervisorctl start fireflies
sudo supervisorctl status fireflies

# Se estiver rodando manualmente
python manage.py runserver 0.0.0.0:8000
```

## 🌐 Configuração do Servidor Web

### **Nginx (Recomendado)**

Edite o arquivo de configuração do Nginx:

```bash
sudo nano /etc/nginx/sites-available/fireflies
```

Adicione ou atualize estas configurações:

```nginx
server {
    listen 80;
    server_name seudominio.com www.seudominio.com;
    
    # Redirecionar para HTTPS (se estiver usando SSL)
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
        alias /caminho/para/fireflies/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Arquivos de mídia
    location /media/ {
        alias /caminho/para/fireflies/media/;
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

Reinicie o Nginx:

```bash
sudo nginx -t  # Testar configuração
sudo systemctl reload nginx
```

### **Apache**

Se estiver usando Apache, crie ou edite o arquivo `.htaccess`:

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

## 🔍 Verificação Pós-Correção

### **1. Testar URLs**
```bash
# Testar arquivos estáticos
curl -I https://seudominio.com/static/css/main.css

# Testar arquivos de mídia
curl -I https://seudominio.com/media/articles/images/test.jpg

# Testar TinyMCE
curl -I https://seudominio.com/tinymce/
```

### **2. Verificar Logs**
```bash
# Logs do Django
tail -f logs/django.log

# Logs do servidor web
tail -f /var/log/nginx/error.log  # Nginx
# ou
tail -f /var/log/apache2/error.log  # Apache
```

### **3. Testar Funcionalidades**
1. Acesse `https://seudominio.com/admin/`
2. Tente criar um artigo com imagem
3. Verifique se o TinyMCE carrega
4. Teste o upload de arquivos

## 🛠️ Solução de Problemas

### **Problema: Mídia ainda não carrega**
```bash
# Verificar se o diretório existe
ls -la media/

# Verificar permissões
ls -la media/

# Verificar se o Django está servindo
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MEDIA_ROOT)
>>> print(settings.MEDIA_URL)
```

### **Problema: TinyMCE não carrega**
```bash
# Verificar se os arquivos estáticos foram coletados
ls -la staticfiles/tinymce/

# Verificar logs do navegador
# Abra o console do navegador (F12) e veja se há erros
```

### **Problema: Erro 500**
```bash
# Verificar logs
tail -f logs/django.log

# Verificar configurações
python manage.py check

# Testar em modo debug temporariamente
export DEBUG=True
python manage.py runserver 0.0.0.0:8000
```

## 📞 Comandos de Emergência

### **Se algo der errado:**
```bash
# Reverter para configuração anterior
git checkout HEAD~1 core/urls.py
git checkout HEAD~1 core/settings.py

# Ou restaurar backup (se tiver)
cp backup/urls.py core/urls.py
cp backup/settings.py core/settings.py

# Reiniciar servidor
sudo systemctl restart fireflies
sudo systemctl reload nginx
```

### **Verificar status dos serviços:**
```bash
# Status do Django
sudo systemctl status fireflies

# Status do Nginx
sudo systemctl status nginx

# Status do Apache (se estiver usando)
sudo systemctl status apache2
```

---

**🎯 Após aplicar estas correções, seu FireFlies CMS deve funcionar corretamente em produção!** 