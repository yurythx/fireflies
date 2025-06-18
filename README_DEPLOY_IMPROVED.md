# 🚀 FireFlies - Sistema de Deploy Automatizado Melhorado

Sistema de deploy modular, robusto e inteligente para o projeto FireFlies, com validações avançadas, health checks e monitoramento contínuo.

## 📋 Índice

- [Características](#-características)
- [Instalação](#-instalação)
- [Uso Básico](#-uso-básico)
- [Comandos Disponíveis](#-comandos-disponíveis)
- [Configuração](#-configuração)
- [Módulos](#-módulos)
- [Health Checks](#-health-checks)
- [Monitoramento](#-monitoramento)
- [Backup e Restore](#-backup-e-restore)
- [Troubleshooting](#-troubleshooting)
- [Exemplos](#-exemplos)

## ✨ Características

### 🔧 **Modular e Extensível**
- Arquitetura modular com separação clara de responsabilidades
- Módulos independentes para cada funcionalidade
- Fácil manutenção e extensão

### 🛡️ **Validações Robustas**
- Verificação automática de pré-requisitos
- Validação de configurações de segurança
- Detecção de problemas antes do deploy

### 🏥 **Health Checks Inteligentes**
- Verificação completa da saúde do sistema
- Health checks específicos por componente
- Monitoramento contínuo opcional

### 🔄 **Deploy Inteligente**
- Detecção automática de ambiente
- Gerenciamento automático de portas
- Backup automático antes do deploy

### 📊 **Logging Avançado**
- Logs coloridos e estruturados
- Diferentes níveis de log
- Rotação automática de logs

### 🎯 **Wizard de Configuração**
- Interface moderna e responsiva
- Validações em tempo real
- Configuração passo-a-passo

## 🚀 Instalação

### Pré-requisitos

```bash
# Docker e Docker Compose
docker --version
docker-compose --version

# Ferramentas do sistema
curl --version
wget --version
git --version
```

### Instalação Rápida

```bash
# 1. Clone o repositório (se ainda não fez)
git clone <repository-url>
cd fireflies

# 2. Torne o script executável
chmod +x deploy_improved.sh

# 3. Execute o deploy
./deploy_improved.sh
```

## 📖 Uso Básico

### Deploy Automático

```bash
# Deploy automático (detecta ambiente)
./deploy_improved.sh

# Deploy em ambiente específico
./deploy_improved.sh -e production
./deploy_improved.sh -e development
./deploy_improved.sh -e staging
```

### Opções Principais

```bash
# Pular validações (para desenvolvimento)
./deploy_improved.sh --skip-validation

# Pular health check
./deploy_improved.sh --skip-health-check

# Forçar deploy
./deploy_improved.sh --force

# Sem backup
./deploy_improved.sh --no-backup

# Com limpeza após deploy
./deploy_improved.sh --cleanup

# Com monitoramento contínuo
./deploy_improved.sh --monitor
```

## 🛠️ Comandos Disponíveis

### Deploy e Health Check

```bash
# Deploy completo
./deploy_improved.sh

# Health check
./deploy_improved.sh health-check
./deploy_improved.sh health

# Health check rápido
./deploy_improved.sh health-check --quick
```

### Backup e Restore

```bash
# Criar backup
./deploy_improved.sh backup

# Restaurar backup
./deploy_improved.sh restore backups/docker/volume_20231201_143022.tar
```

### Monitoramento

```bash
# Monitoramento contínuo
./deploy_improved.sh monitor

# Monitoramento com intervalo personalizado
./deploy_improved.sh monitor 60  # 60 segundos
```

### Logs e Status

```bash
# Ver logs
./deploy_improved.sh logs

# Ver logs de serviço específico
./deploy_improved.sh logs web

# Ver logs com número de linhas
./deploy_improved.sh logs web 200

# Status do sistema
./deploy_improved.sh status
```

### Manutenção

```bash
# Limpeza geral
./deploy_improved.sh cleanup

# Limpeza de logs
./deploy_improved.sh cleanup --logs-only

# Limpeza de Docker
./deploy_improved.sh cleanup --docker-only
```

## ⚙️ Configuração

### Arquivo de Configuração

O sistema usa o arquivo `deploy.config` para configurações:

```bash
# Editar configurações
nano deploy.config
```

### Configurações Principais

```ini
# Ambiente padrão
DEFAULT_ENVIRONMENT=development

# Nível de log (0=DEBUG, 1=INFO, 2=WARNING, 3=ERROR)
LOG_LEVEL=1

# Backup antes do deploy
BACKUP_BEFORE_DEPLOY=true

# Health check após deploy
HEALTH_CHECK_AFTER_DEPLOY=true

# Monitoramento contínuo
ENABLE_MONITORING=false
```

### Configurações por Ambiente

```ini
[development]
DEBUG=true
LOG_LEVEL=0
BACKUP_BEFORE_DEPLOY=false

[production]
DEBUG=false
LOG_LEVEL=2
BACKUP_BEFORE_DEPLOY=true
SECURITY_CHECKS=true
```

## 🧩 Módulos

### 1. **Environment Module** (`environment.sh`)
- Detecção automática de ambiente
- Configuração de variáveis de ambiente
- Detecção de IP da máquina

### 2. **Validation Module** (`validation.sh`)
- Verificação de pré-requisitos
- Validação de configurações
- Verificação de recursos do sistema

### 3. **Docker Module** (`docker.sh`)
- Build de imagens Docker
- Deploy com Docker Compose
- Gerenciamento de portas
- Backup e restore de volumes

### 4. **Health Module** (`health.sh`)
- Health checks completos
- Verificação de conectividade
- Monitoramento de recursos

### 5. **Logging Module** (`logging.sh`)
- Sistema de logging estruturado
- Logs coloridos
- Rotação automática

## 🏥 Health Checks

### Componentes Verificados

1. **Containers Docker**
   - Status de execução
   - Health checks individuais
   - Logs de erro

2. **Aplicação Web**
   - Conectividade HTTP
   - Endpoints de saúde
   - Wizard de configuração

3. **Banco de Dados**
   - Conexão PostgreSQL
   - Tabelas Django
   - Migrations

4. **Cache Redis**
   - Conectividade Redis
   - Comandos básicos

5. **Sistema**
   - Uso de CPU e memória
   - Espaço em disco
   - Conectividade de rede

### Health Check Rápido

```bash
# Para CI/CD
./deploy_improved.sh health-check --quick
```

### Health Check Detalhado

```bash
# Com métricas
./deploy_improved.sh health-check --detailed
```

## 📊 Monitoramento

### Monitoramento Contínuo

```bash
# Iniciar monitoramento
./deploy_improved.sh monitor

# Com intervalo personalizado
./deploy_improved.sh monitor 60
```

### Métricas Coletadas

- Status dos containers
- Uso de recursos do sistema
- Conectividade da aplicação
- Logs de erro

### Alertas

O sistema pode ser configurado para enviar alertas via:
- Email
- Slack
- Webhooks personalizados

## 💾 Backup e Restore

### Backup Automático

```bash
# Backup antes do deploy
./deploy_improved.sh --backup

# Backup manual
./deploy_improved.sh backup
```

### Restore

```bash
# Restaurar backup
./deploy_improved.sh restore backups/docker/volume_20231201_143022.tar
```

### Configurações de Backup

```ini
# Diretório de backup
BACKUP_DIR=backups

# Retenção de backups (dias)
BACKUP_RETENTION_DAYS=7

# Comprimir backups
COMPRESS_BACKUPS=true
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. **Docker não está rodando**
```bash
# Linux
sudo systemctl start docker

# macOS
open -a Docker

# Windows
# Inicie o Docker Desktop
```

#### 2. **Portas ocupadas**
```bash
# Verificar portas em uso
lsof -i :8000
lsof -i :5432
lsof -i :6379

# O sistema tentará portas alternativas automaticamente
```

#### 3. **Permissões de Docker**
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Reiniciar sessão
newgrp docker
```

#### 4. **Logs de erro**
```bash
# Ver logs detalhados
./deploy_improved.sh logs

# Ver logs de erro específicos
./deploy_improved.sh logs web | grep ERROR
```

### Modo Debug

```bash
# Ativar modo debug
export DEPLOY_DEBUG=true
./deploy_improved.sh

# Ou editar deploy.config
DEPLOY_DEBUG=true
```

## 📝 Exemplos

### Exemplo 1: Deploy de Desenvolvimento

```bash
# Deploy rápido para desenvolvimento
./deploy_improved.sh -e development --skip-validation --skip-health-check
```

### Exemplo 2: Deploy de Produção

```bash
# Deploy completo para produção
./deploy_improved.sh -e production --cleanup
```

### Exemplo 3: Monitoramento

```bash
# Deploy + monitoramento contínuo
./deploy_improved.sh -e staging --monitor
```

### Exemplo 4: Backup e Restore

```bash
# Backup antes de atualização
./deploy_improved.sh backup

# Deploy da atualização
./deploy_improved.sh -e production

# Se algo der errado, restaurar
./deploy_improved.sh restore backups/docker/volume_20231201_143022.tar
```

### Exemplo 5: Health Check Contínuo

```bash
# Verificar saúde a cada 30 segundos
./deploy_improved.sh monitor 30
```

## 🎯 Wizard de Configuração

### Acesso ao Wizard

Após o primeiro deploy, acesse:
```
http://localhost:8000/config/setup/
```

### Funcionalidades do Wizard

- **Configuração de Banco de Dados**
  - Detecção automática de bancos
  - Teste de conectividade
  - Configuração de credenciais

- **Configuração de Email**
  - Setup de SMTP
  - Teste de envio
  - Templates de email

- **Configuração de Módulos**
  - Ativação de módulos
  - Configuração de permissões
  - Setup inicial

- **Configuração de Segurança**
  - Geração de SECRET_KEY
  - Configuração de ALLOWED_HOSTS
  - Setup de SSL

## 🔒 Segurança

### Validações de Segurança

- Verificação de SECRET_KEY em produção
- Validação de DEBUG=False em produção
- Verificação de ALLOWED_HOSTS
- Validação de configurações de SSL

### Boas Práticas

1. **Nunca use DEBUG=True em produção**
2. **Altere a SECRET_KEY padrão**
3. **Configure ALLOWED_HOSTS adequadamente**
4. **Use HTTPS em produção**
5. **Mantenha backups regulares**

## 📈 Performance

### Otimizações Automáticas

- Cache Docker otimizado
- Build paralelo quando possível
- Limpeza automática de recursos
- Rotação de logs

### Monitoramento de Performance

```bash
# Ver estatísticas dos containers
./deploy_improved.sh status

# Monitorar recursos
./deploy_improved.sh monitor
```

## 🤝 Contribuição

### Estrutura de Módulos

Para adicionar um novo módulo:

1. Crie o arquivo em `scripts/deploy/modules/`
2. Implemente as funções necessárias
3. Importe no `deploy_improved.sh`
4. Documente as funcionalidades

### Padrões de Código

- Use funções com nomes descritivos
- Implemente logging adequado
- Adicione validações de erro
- Documente parâmetros e retornos

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🆘 Suporte

### Logs e Debug

```bash
# Ver logs detalhados
tail -f logs/deploy_*.log

# Modo debug
DEPLOY_DEBUG=true ./deploy_improved.sh
```

### Issues e Problemas

1. Verifique os logs em `logs/`
2. Execute health check: `./deploy_improved.sh health-check`
3. Verifique status: `./deploy_improved.sh status`
4. Consulte a documentação
5. Abra uma issue no repositório

---

**FireFlies Deploy System** - Deploy inteligente e automatizado para aplicações Django modernas. 