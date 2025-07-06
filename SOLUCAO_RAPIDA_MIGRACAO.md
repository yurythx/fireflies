# 🚀 Solução Rápida - Erro de Migração em Produção

## ❌ Problema
```
ProgrammingError at /artigos/
column articles_article.image_caption does not exist
```

## 🔍 Diagnóstico
A migração `0003_article_image_caption.py` não foi aplicada no banco de dados de produção.

## ✅ Soluções (Escolha uma)

### **Opção 1: Comando Django (Recomendado)**

```bash
# 1. Acesse o servidor de produção
ssh seu-usuario@34.82.179.160

# 2. Navegue para o diretório do projeto
cd /var/www/fireflies

# 3. Ative o ambiente virtual
source env/bin/activate

# 4. Execute o comando de correção
python manage.py fix_migration_issues --specific-migration articles.0003_article_image_caption --force
```

### **Opção 2: Script Python**

```bash
# 1. Acesse o servidor de produção
ssh seu-usuario@34.82.179.160

# 2. Navegue para o diretório do projeto
cd /var/www/fireflies

# 3. Ative o ambiente virtual
source env/bin/activate

# 4. Execute o script de correção
python fix_migration_production.py
```

### **Opção 3: Script de Deploy Melhorado**

```bash
# 1. Acesse o servidor de produção
ssh seu-usuario@34.82.179.160

# 2. Navegue para o diretório do projeto
cd /var/www/fireflies

# 3. Execute o script de deploy com correção
chmod +x deploy_production_fix.sh
./deploy_production_fix.sh
```

### **Opção 4: Correção Manual (Último recurso)**

```bash
# 1. Acesse o servidor de produção
ssh seu-usuario@34.82.179.160

# 2. Navegue para o diretório do projeto
cd /var/www/fireflies

# 3. Ative o ambiente virtual
source env/bin/activate

# 4. Execute comandos manualmente
python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('ALTER TABLE articles_article ADD COLUMN image_caption VARCHAR(255) DEFAULT \"\" NOT NULL')
    print('✅ Coluna criada')
    
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO django_migrations (app, name, applied) VALUES (\"articles\", \"0003_article_image_caption\", NOW()) ON CONFLICT (app, name) DO NOTHING')
    print('✅ Migração marcada como aplicada')
    
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

## 🔧 Verificação

Após aplicar a correção, verifique se funcionou:

```bash
# Testar se a coluna existe
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_name = \"articles_article\" AND column_name = \"image_caption\"')
    result = cursor.fetchone()
    if result:
        print('✅ Coluna image_caption existe')
    else:
        print('❌ Coluna image_caption NÃO existe')
"

# Testar se a view funciona
python manage.py shell -c "
from django.test import Client
client = Client()
response = client.get('/artigos/')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    print('✅ View funcionando')
else:
    print('❌ View com problema')
"
```

## 🚀 Reiniciar Serviços

Após a correção, reinicie os serviços:

```bash
# Se estiver usando systemd
sudo systemctl restart fireflies

# Se estiver usando Docker
docker-compose restart web

# Verificar status
sudo systemctl status fireflies
```

## 📊 Monitoramento

Verifique se tudo está funcionando:

```bash
# Verificar logs
tail -f /var/log/fireflies.log

# Testar endpoint
curl -I http://34.82.179.160/artigos/

# Verificar saúde
curl http://34.82.179.160/health/
```

## 🛡️ Prevenção

Para evitar problemas futuros:

### **1. Adicionar ao script de deploy**

```bash
# Sempre executar migrações antes do deploy
python manage.py migrate --noinput

# Verificar se não há problemas
python manage.py check --deploy
```

### **2. Comando de verificação periódica**

```bash
# Adicionar ao crontab para verificar diariamente
0 2 * * * cd /var/www/fireflies && source env/bin/activate && python manage.py fix_migration_issues --check-only
```

### **3. Backup automático**

```bash
# Backup antes de migrações
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
```

## 🆘 Se nada funcionar

### **1. Restaurar backup**
```bash
# Se você tem um backup recente
cp db.sqlite3.backup.20250706_133800 db.sqlite3
```

### **2. Recriar banco (CUIDADO - perde dados)**
```bash
# ÚLTIMO RECURSO - perde todos os dados
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### **3. Contatar suporte**
- Verificar logs completos
- Documentar passos executados
- Fornecer output dos comandos

## 📋 Checklist de Solução

- [ ] Identificar o problema (coluna não existe)
- [ ] Escolher método de correção
- [ ] Executar correção
- [ ] Verificar se funcionou
- [ ] Reiniciar serviços
- [ ] Testar aplicação
- [ ] Documentar solução
- [ ] Implementar prevenção

## 🎯 Resultado Esperado

Após a correção:
- ✅ `/artigos/` deve retornar status 200
- ✅ Coluna `image_caption` deve existir no banco
- ✅ Migração deve estar marcada como aplicada
- ✅ Aplicação deve funcionar normalmente

---

**⏱️ Tempo estimado**: 5-10 minutos  
**🛠️ Complexidade**: Baixa  
**⚠️ Risco**: Baixo (com backup)  
**📞 Suporte**: Se precisar de ajuda, forneça os logs de erro 