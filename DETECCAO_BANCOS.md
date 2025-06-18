# 🔍 Detecção Automática de Bancos - FireFlies

## Visão Geral

O wizard de configuração do FireFlies agora inclui **detecção automática de bancos** para SQLite, PostgreSQL e MySQL, mostrando informações detalhadas sobre os bancos encontrados no sistema.

## ✨ Funcionalidades Implementadas

### 🔍 Detecção Inteligente de Bancos
- **SQLite**: Detecta arquivos .sqlite3, .db e .sqlite
- **PostgreSQL**: Detecta instâncias e bancos disponíveis
- **MySQL**: Detecta instâncias e bancos disponíveis
- **Informações detalhadas**: Tamanho, número de tabelas, tipo de banco

### 🌐 Informações Detectadas

#### SQLite
- ✅ **Caminho do arquivo** (absoluto e relativo)
- ✅ **Tamanho do arquivo** (formatado)
- ✅ **Número de tabelas**
- ✅ **Validação de integridade**

#### PostgreSQL
- ✅ **Host e porta** da instância
- ✅ **Lista de bancos** disponíveis
- ✅ **Tamanho de cada banco** (formatado)
- ✅ **Número de tabelas** por banco
- ✅ **Detecção de bancos Django** (auth_user, django_migrations, etc.)

#### MySQL
- ✅ **Host e porta** da instância
- ✅ **Lista de bancos** disponíveis (excluindo bancos do sistema)
- ✅ **Tamanho de cada banco** (em MB)
- ✅ **Número de tabelas** por banco
- ✅ **Detecção de bancos Django** (auth_user, django_migrations, etc.)

## 🚀 Como Funciona

### 1. Detecção Automática
O wizard detecta automaticamente:
- **Instâncias rodando** em portas comuns
- **Bancos existentes** em cada instância
- **Informações detalhadas** de cada banco

### 2. Interface Intuitiva
- **Lista visual** de bancos detectados
- **Informações detalhadas** para cada banco
- **Seleção com um clique** para usar banco existente
- **Indicadores visuais** para bancos Django

### 3. Preenchimento Automático
- **Campos preenchidos** automaticamente ao selecionar banco
- **Credenciais** ainda precisam ser inseridas manualmente
- **Validação** de conexão antes de prosseguir

## 📋 Exemplo de Interface

### SQLite Detectado
```
📁 db.sqlite3
   Caminho: ./db.sqlite3
   15 tabelas • 2.5 MB
   [Usar] [Criar Novo]
```

### PostgreSQL Detectado
```
🗄️ localhost:5432
   3 banco(s) disponível(is)
   [Usar Instância]
   
   📊 fireflies_prod
      Django 25 tabelas • 15.2 MB
      [Usar Banco]
   
   📊 test_db
      8 tabelas • 2.1 MB
      [Usar Banco]
```

### MySQL Detectado
```
🗄️ localhost:3306
   2 banco(s) disponível(is)
   [Usar Instância]
   
   📊 myapp_db
      Django 18 tabelas • 8.7 MB
      [Usar Banco]
   
   📊 legacy_db
      12 tabelas • 5.3 MB
      [Usar Banco]
```

## 🔧 Configuração de Portas

### PostgreSQL
- **Porta padrão**: 5432
- **Portas alternativas**: 5433, 5434
- **Hosts testados**: localhost, 127.0.0.1

### MySQL
- **Porta padrão**: 3306
- **Portas alternativas**: 3307, 3308
- **Hosts testados**: localhost, 127.0.0.1

## 🎯 Casos de Uso

### Desenvolvimento
```bash
# Banco SQLite local detectado automaticamente
./deploy.sh
# Wizard mostra: "db.sqlite3 - 15 tabelas • 2.5 MB"
```

### Produção com PostgreSQL
```bash
# Instância PostgreSQL detectada
./deploy.sh --env production
# Wizard mostra: "localhost:5432 - 3 bancos disponíveis"
```

### Migração de Banco
```bash
# Banco MySQL existente detectado
./deploy.sh
# Wizard mostra: "myapp_db - Django 18 tabelas • 8.7 MB"
```

## 🔍 Detecção de Bancos Django

O sistema identifica automaticamente bancos Django pela presença de tabelas específicas:

### Tabelas Verificadas
- `auth_user` (sistema de autenticação)
- `django_migrations` (controle de migrações)
- `django_content_type` (tipos de conteúdo)

### Indicador Visual
- **Badge "Django"** verde para bancos identificados
- **Informações detalhadas** sobre estrutura
- **Recomendação** para reutilização

## 📊 Informações Coletadas

### Para Cada Banco
```python
{
    'name': 'nome_do_banco',
    'tables_count': 25,
    'size': '15.2 MB',
    'is_django': True,
    'is_valid': True,
}
```

### Para Cada Instância
```python
{
    'host': 'localhost',
    'port': 5432,
    'databases': [lista_de_bancos],
    'is_accessible': True,
}
```

## 🚀 Benefícios

### ✅ Facilidade de Uso
- **Zero configuração manual** de conexão
- **Detecção automática** de bancos existentes
- **Interface intuitiva** para seleção

### ✅ Informações Detalhadas
- **Tamanho dos bancos** formatado
- **Número de tabelas** por banco
- **Identificação de Django** automática

### ✅ Segurança
- **Validação de conexão** antes do uso
- **Teste de credenciais** obrigatório
- **Fallback** para criação de novos bancos

### ✅ Compatibilidade
- **Múltiplas portas** testadas
- **Diferentes usuários** (postgres, root)
- **Tratamento de erros** robusto

## 🔧 Configuração Avançada

### Adicionar Novas Portas
```python
# Em setup_views.py
common_ports = [5432, 5433, 5434, 5435]  # Adicionar nova porta
```

### Adicionar Novos Hosts
```python
# Em setup_views.py
common_hosts = ['localhost', '127.0.0.1', '192.168.1.100']
```

### Personalizar Detecção Django
```python
# Em setup_views.py
django_tables = ['auth_user', 'django_migrations', 'django_content_type', 'custom_table']
```

## 🐛 Troubleshooting

### Banco Não Detectado
```bash
# Verificar se o serviço está rodando
sudo systemctl status postgresql
sudo systemctl status mysql

# Verificar portas
sudo netstat -tlnp | grep :5432
sudo netstat -tlnp | grep :3306
```

### Erro de Conexão
```bash
# Verificar credenciais
psql -h localhost -U postgres
mysql -h localhost -u root -p

# Verificar firewall
sudo ufw status
```

### Banco Django Não Identificado
```bash
# Verificar tabelas
psql -d nome_do_banco -c "\dt"
mysql -u root -p nome_do_banco -e "SHOW TABLES;"
```

## 📈 Próximas Melhorias

- [ ] Detecção de bancos remotos
- [ ] Backup automático antes de usar banco existente
- [ ] Migração automática de dados
- [ ] Detecção de versão do Django
- [ ] Análise de compatibilidade de esquemas

---

**FireFlies** - Sistema de gerenciamento de conteúdo com detecção automática de bancos 🚀

**Funcionalidades de Banco:**
- 🔍 Detecção automática de SQLite, PostgreSQL e MySQL
- 📊 Informações detalhadas de cada banco
- 🎯 Identificação automática de bancos Django
- 🚀 Seleção com um clique para reutilização
- 🔒 Validação de conexão e segurança 