# 🚀 Guia do Setup Wizard - FireFlies

## Visão Geral

O FireFlies agora possui um sistema de configuração pós-deploy similar ao Zabbix e GLPI, que permite configurar o banco de dados e outras configurações após a primeira instalação. Isso torna o deploy mais flexível e seguro.

## 🎯 Como Funciona

### 1. **Primeira Instalação**
- O sistema detecta automaticamente se é a primeira instalação
- Cria um arquivo `.first_install` para marcar o estado
- Redireciona automaticamente para o wizard de configuração

### 2. **Wizard de Configuração**
- **Passo 1**: Configuração do banco de dados (SQLite, PostgreSQL, MySQL)
- **Passo 2**: Criação do usuário administrador
- **Passo 3**: Configuração de email
- **Passo 4**: Finalização e aplicação das configurações

### 3. **Configuração Automática**
- Aplica todas as configurações automaticamente
- Remove o arquivo `.first_install`
- Sistema fica pronto para uso

## 📋 Pré-requisitos

### Para Deploy Inicial
```bash
# Linux/Mac
./deploy.sh

# Windows
.\deploy.ps1
```

### Para Configuração Manual
```bash
# Marcar como primeira instalação
python manage.py create_first_install

# Remover modo primeira instalação
python manage.py create_first_install --remove
```

## 🔧 Configuração do Banco de Dados

### SQLite (Padrão)
- **Vantagens**: Simples, não requer configuração adicional
- **Uso**: Desenvolvimento e pequenos projetos
- **Configuração**: Automática

### PostgreSQL
- **Vantagens**: Robusto, escalável, ACID
- **Uso**: Produção e projetos médios/grandes
- **Configuração**:
  - Host: `localhost` (ou IP do servidor)
  - Porta: `5432`
  - Nome do banco: `fireflies`
  - Usuário e senha: Configurados pelo usuário

### MySQL
- **Vantagens**: Popular, bem suportado
- **Uso**: Produção e projetos com MySQL existente
- **Configuração**:
  - Host: `localhost` (ou IP do servidor)
  - Porta: `3306`
  - Nome do banco: `fireflies`
  - Usuário e senha: Configurados pelo usuário

## 👤 Usuário Administrador

### Requisitos
- **Nome de usuário**: Único no sistema
- **Email**: Válido e único
- **Senha**: Mínimo 8 caracteres
- **Confirmação**: Senha deve ser confirmada

### Permissões
- Acesso total ao sistema
- Criação de outros usuários
- Configuração de módulos
- Acesso ao admin do Django

## 📧 Configuração de Email

### Console (Desenvolvimento)
- **Backend**: `django.core.mail.backends.console.EmailBackend`
- **Uso**: Desenvolvimento e testes
- **Funcionalidade**: Emails aparecem no console

### SMTP (Produção)
- **Backend**: `django.core.mail.backends.smtp.EmailBackend`
- **Configuração**:
  - Servidor SMTP: `smtp.gmail.com`, `smtp.office365.com`, etc.
  - Porta: `587` (TLS) ou `465` (SSL)
  - TLS: Habilitado por padrão
  - Usuário e senha: Credenciais do provedor

## 🔄 Fluxo de Deploy

### 1. Deploy Inicial
```bash
# Executar deploy
./deploy.sh

# Sistema detecta primeira instalação
# Cria arquivo .first_install
# Redireciona para setup wizard
```

### 2. Configuração via Wizard
1. Acesse `http://localhost:8000/`
2. Configure banco de dados
3. Crie usuário administrador
4. Configure email
5. Finalize configuração

### 3. Sistema Pronto
- Arquivo `.first_install` removido
- Configurações aplicadas
- Sistema funcionando normalmente

## 🛠️ Comandos Úteis

### Gerenciar Primeira Instalação
```bash
# Marcar como primeira instalação
python manage.py create_first_install

# Forçar recriação
python manage.py create_first_install --force

# Remover modo primeira instalação
python manage.py create_first_install --remove
```

### Verificar Status
```bash
# Verificar se é primeira instalação
ls -la .first_install

# Verificar configurações
python manage.py shell -c "from django.conf import settings; print(settings.DATABASES)"
```

## 🔒 Segurança

### Proteções Implementadas
- **CSRF Protection**: Todos os formulários protegidos
- **Validação de Dados**: Campos obrigatórios e formatos
- **Teste de Conexão**: Validação antes de salvar
- **Arquivos Temporários**: Limpeza automática
- **Middleware de Redirecionamento**: URLs protegidas

### URLs Protegidas
- `/config/setup/` - Wizard de configuração
- `/config/setup/api/` - API do wizard
- `/health/` - Health checks
- `/static/` - Arquivos estáticos
- `/media/` - Arquivos de mídia
- `/admin/` - Admin do Django

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. **Wizard não aparece**
```bash
# Verificar se arquivo .first_install existe
ls -la .first_install

# Recriar se necessário
python manage.py create_first_install --force
```

#### 2. **Erro de conexão com banco**
- Verificar se o banco está rodando
- Verificar credenciais
- Verificar firewall/portas
- Testar conexão manualmente

#### 3. **Erro de permissões**
```bash
# Verificar permissões de arquivos
chmod 755 .first_install
chmod 644 .env
```

#### 4. **Loop de redirecionamento**
- Verificar middleware de setup
- Verificar URLs de exceção
- Limpar cache do navegador

### Logs e Debug
```bash
# Verificar logs do Django
tail -f logs/django.log

# Debug do setup
python manage.py shell -c "
from pathlib import Path
print('First install file exists:', Path('.first_install').exists())
"
```

## 📚 Exemplos de Uso

### Deploy Completo
```bash
# 1. Deploy inicial
./deploy.sh

# 2. Acessar wizard
# http://localhost:8000/

# 3. Configurar PostgreSQL
# Host: localhost
# Porta: 5432
# Banco: fireflies
# Usuário: fireflies_user
# Senha: fireflies_password

# 4. Criar admin
# Usuário: admin
# Email: admin@exemplo.com
# Senha: admin123456

# 5. Configurar email
# Backend: SMTP
# Servidor: smtp.gmail.com
# Porta: 587
# TLS: Sim
# Usuário: seu-email@gmail.com
# Senha: sua-senha-app

# 6. Finalizar
# Sistema pronto!
```

### Migração de Banco
```bash
# 1. Marcar como primeira instalação
python manage.py create_first_install

# 2. Acessar wizard
# http://localhost:8000/

# 3. Configurar novo banco
# 4. Finalizar configuração
```

## 🔄 Migração de Dados

### Backup Antes da Migração
```bash
# Backup do banco atual
python manage.py dumpdata > backup.json

# Backup de arquivos
tar -czf media_backup.tar.gz media/
```

### Restauração Após Migração
```bash
# Restaurar dados
python manage.py loaddata backup.json

# Restaurar arquivos
tar -xzf media_backup.tar.gz
```

## 📈 Monitoramento

### Health Checks
```bash
# Verificar saúde do sistema
curl http://localhost:8000/health/

# Verificar readiness
curl http://localhost:8000/health/ready/

# Verificar liveness
curl http://localhost:8000/health/live/
```

### Métricas
- Tempo de configuração
- Taxa de sucesso
- Erros comuns
- Performance do banco

## 🎉 Conclusão

O sistema de configuração pós-deploy do FireFlies oferece:

✅ **Flexibilidade**: Configure após o deploy
✅ **Segurança**: Validação e proteções
✅ **Simplicidade**: Interface intuitiva
✅ **Robustez**: Múltiplos bancos suportados
✅ **Monitoramento**: Health checks integrados

Este sistema torna o FireFlies mais profissional e fácil de configurar, similar aos melhores sistemas open-source disponíveis. 