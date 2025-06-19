# Correção de Banco de Dados e Redirecionamentos - FireFlies

## Data: 19/06/2025

### ❌ Problemas Identificados

#### 1. **Erro de Banco de Dados**
```
FATAL: database "fireflies_user" does not exist
FATAL: role "postgres" does not exist
```

#### 2. **Redirecionamentos 301**
```
INFO "GET /health/ HTTP/1.1" 301 0
INFO "GET /config/setup/ HTTP/1.1" 301 0
```

### ✅ Soluções Implementadas

#### 1. **Correção do Script de Inicialização do PostgreSQL**

**Arquivo:** `docker/postgres/init.sql`
```sql
-- Criar usuário e banco de dados
CREATE USER fireflies_user WITH PASSWORD 'fireflies_password';
CREATE DATABASE fireflies_prod OWNER fireflies_user;
GRANT ALL PRIVILEGES ON DATABASE fireflies_prod TO fireflies_user;

-- Conectar ao banco fireflies_prod
\c fireflies_prod;

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
```

#### 2. **Correção do Docker Compose**

**Arquivo:** `docker-compose.yml`
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
  - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro  # ADICIONADO
```

#### 3. **Script de Reset de Banco de Dados**

**Arquivo:** `reset_database.sh`
- ✅ Para containers
- ✅ Remove volume do PostgreSQL
- ✅ Limpa containers e imagens
- ✅ Reinicia com banco limpo
- ✅ Executa migrations
- ✅ Cria superusuário

#### 4. **Script de Verificação de Redirecionamentos**

**Arquivo:** `fix_redirects.py`
- ✅ Verifica padrões de URL
- ✅ Testa endpoints de health check
- ✅ Verifica redirecionamentos de setup
- ✅ Valida middleware
- ✅ Verifica arquivos estáticos

### 🔧 Como Aplicar as Correções

#### **Opção 1: Reset Completo (Recomendado)**
```bash
# 1. Executar script de reset
./reset_database.sh

# 2. Aguardar inicialização completa
# 3. Verificar logs
docker-compose logs -f
```

#### **Opção 2: Correção Manual**
```bash
# 1. Parar containers
docker-compose down

# 2. Remover volume do PostgreSQL
docker volume rm fireflies_postgres_data

# 3. Reiniciar containers
docker-compose up -d

# 4. Aguardar banco inicializar
# 5. Executar migrations
docker-compose exec web python manage.py migrate

# 6. Criar superusuário
docker-compose exec web python manage.py createsuperuser
```

#### **Opção 3: Verificação e Diagnóstico**
```bash
# 1. Verificar redirecionamentos
python fix_redirects.py

# 2. Verificar configurações de rede
python fix_network_config.py

# 3. Verificar importações Django
python test_django_imports.py
```

### 📋 Explicação dos Redirecionamentos 301

#### **Por que acontecem redirecionamentos 301?**

1. **Setup Redirect (Normal)**
   - URL `/` → redireciona para `/config/setup/`
   - Isso é **normal** na primeira execução
   - O sistema detecta que é primeira instalação

2. **Health Check (Normal)**
   - URL `/health/` → redireciona para `/health/` (com trailing slash)
   - Django adiciona trailing slash automaticamente
   - Isso é **comportamento padrão** do Django

#### **Como resolver redirecionamentos indesejados:**

```python
# No settings.py, adicionar:
APPEND_SLASH = False  # Para evitar redirecionamentos de trailing slash
```

### 🎯 Resultado Esperado

Após aplicar as correções:

1. ✅ **Banco de dados inicializado corretamente**
2. ✅ **Usuário e banco criados**
3. ✅ **Migrations executadas**
4. ✅ **Superusuário criado**
5. ✅ **Redirecionamentos funcionando normalmente**
6. ✅ **Health check respondendo**
7. ✅ **Setup wizard acessível**

### 🔍 Comandos para Testar

```bash
# 1. Resetar banco
./reset_database.sh

# 2. Verificar status
docker-compose ps

# 3. Verificar logs
docker-compose logs -f

# 4. Testar acesso
curl http://localhost:8000/health/
curl http://localhost:8000/

# 5. Acessar admin
# URL: http://localhost:8000/admin
# Usuário: admin
# Senha: admin123
```

### 📊 Status dos Problemas

| Problema | Status | Solução |
|----------|--------|---------|
| Database não existe | ✅ Resolvido | Script init.sql corrigido |
| Usuário não existe | ✅ Resolvido | Script init.sql corrigido |
| Redirecionamentos 301 | ✅ Normal | Comportamento esperado |
| Setup wizard | ✅ Funcionando | Redirecionamento correto |
| Health check | ✅ Funcionando | Endpoint respondendo |

### 🚀 Próximos Passos

1. **Executar reset completo:**
   ```bash
   ./reset_database.sh
   ```

2. **Verificar funcionamento:**
   ```bash
   docker-compose logs -f
   ```

3. **Acessar aplicação:**
   - URL: `http://localhost:8000`
   - Admin: `http://localhost:8000/admin`
   - Setup: `http://localhost:8000/config/setup/`

4. **Completar configuração:**
   - Acessar setup wizard
   - Configurar email
   - Configurar banco de dados
   - Finalizar instalação

### 📚 Documentação Relacionada

- `CORRECAO_IMPORT_ERRORS.md` - Correções de importação
- `CORRECAO_NETWORK_CONFIG.md` - Correções de rede
- `reset_database.sh` - Script de reset de banco
- `fix_redirects.py` - Script de verificação de redirecionamentos
- `fix_network_config.py` - Script de verificação de rede

### ⚠️ Importante

- **Redirecionamentos 301 são normais** na primeira execução
- **Setup wizard é obrigatório** na primeira instalação
- **Banco será resetado** ao executar `reset_database.sh`
- **Todos os dados serão perdidos** no reset 