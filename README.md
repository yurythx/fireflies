# 🦟 FireFlies - Sistema de Deploy Automatizado

Um sistema Django moderno com deploy automatizado que detecta o ambiente e realiza deploy de forma inteligente, inspirado no tema dos Fireflies de The Last of Us.

## 🚀 Características

- **Deploy Automatizado**: Detecta automaticamente o ambiente (development/staging/production)
- **Docker Integration**: Containers otimizados para cada ambiente
- **Tema FireFlies**: Interface escura com efeitos de brilho verde/amarelo
- **Módulos Dinâmicos**: Sistema de módulos configurável
- **Multi-ambiente**: Suporte para development, staging e production
- **Health Checks**: Verificação automática de saúde da aplicação
- **Logs Estruturados**: Sistema de logging profissional

## 📋 Pré-requisitos

- Python 3.8+
- Docker e Docker Compose
- Git (opcional)

## 🛠️ Instalação Rápida

### 1. Clone o repositório
```bash
git clone <repository-url>
cd fireflies
```

### 2. Deploy Automatizado (Recomendado)

#### Linux/macOS:
```bash
# Deploy automático (detecta ambiente)
chmod +x deploy.sh
./deploy.sh

# Ou especificar ambiente
./deploy.sh --env development
./deploy.sh --env staging
./deploy.sh --env production
```

#### Windows:
```powershell
# Deploy automático (detecta ambiente)
.\deploy.ps1

# Ou especificar ambiente
.\deploy.ps1 -Environment development
.\deploy.ps1 -Environment staging
.\deploy.ps1 -Environment production
```

### 3. Usando Makefile (Alternativo)

```bash
# Verificar pré-requisitos
make check

# Setup completo para desenvolvimento
make dev-setup

# Deploy em desenvolvimento
make dev

# Deploy em produção
make prod

# Deploy automático
make deploy
```

## 🔧 Comandos Principais

### Deploy
```bash
# Deploy automático (detecta ambiente)
./deploy.sh                    # Linux/macOS
.\deploy.ps1                   # Windows

# Deploy específico
./deploy.sh --env production   # Linux/macOS
.\deploy.ps1 -Environment production  # Windows

# Deploy forçado (ignora erros)
./deploy.sh --force            # Linux/macOS
.\deploy.ps1 -Force            # Windows
```

### Verificação
```bash
# Verificar pré-requisitos
./deploy.sh --check-only       # Linux/macOS
.\deploy.ps1 -CheckOnly        # Windows

# Verificar saúde da aplicação
make health

# Verificar status dos containers
make status
```

### Manutenção
```bash
# Parar containers
make stop

# Limpar recursos
make clean

# Reset completo
make reset

# Rebuild completo
make rebuild
```

### Logs e Monitoramento
```bash
# Ver logs
make logs

# Monitorar recursos
make monitor

# Monitorar em tempo real
make watch
```

## 🌍 Ambientes

### Development
- Debug ativado
- Hot reload
- Logs detalhados
- Docker Compose dev

### Staging
- Debug desativado
- Collect static
- Otimizações básicas
- Docker Compose prod

### Production
- Debug desativado
- Collect static
- Otimizações completas
- Health checks rigorosos

## 🔍 Detecção Automática de Ambiente

O sistema detecta automaticamente o ambiente baseado em:

1. **Variável de ambiente**: `ENVIRONMENT=production`
2. **Plataforma**: Heroku, Kubernetes, Docker
3. **Branch Git**: main/master = production, staging = staging
4. **Padrão**: development

## 📁 Estrutura do Projeto

```
fireflies/
├── apps/                    # Aplicações Django
│   ├── accounts/           # Sistema de usuários
│   ├── articles/           # Sistema de artigos
│   ├── config/             # Configurações e módulos
│   └── pages/              # Páginas estáticas
├── core/                   # Configurações Django
├── static/                 # Arquivos estáticos
├── media/                  # Uploads
├── docker/                 # Configurações Docker
├── deploy.sh              # Script de deploy (Linux/macOS)
├── deploy.ps1             # Script de deploy (Windows)
├── Makefile               # Comandos Make
└── README.md              # Este arquivo
```

## 🐳 Docker

### Containers
- **Web**: Aplicação Django
- **Database**: PostgreSQL (opcional)
- **Redis**: Cache e sessões
- **Nginx**: Proxy reverso

### Comandos Docker
```bash
# Build da imagem
docker build -t fireflies:latest .

# Executar container
docker run -p 8000:8000 fireflies:latest

# Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)
```env
ENVIRONMENT=development
DEBUG=true
DJANGO_SETTINGS_MODULE=core.settings_dev
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### Módulos
O sistema suporta módulos dinâmicos:
- **accounts**: Sistema de usuários
- **articles**: Sistema de artigos
- **config**: Configurações
- **pages**: Páginas estáticas

## 🧪 Testes

```bash
# Executar testes
make test

# Testes com cobertura
python -m pytest --cov

# Testes específicos
python manage.py test apps.accounts
```

## 📊 Monitoramento

### Health Check
```bash
# Verificar saúde
curl http://localhost:8000/health/

# Via Makefile
make health
```

### Logs
```bash
# Logs da aplicação
make logs

# Logs específicos
docker-compose logs web
docker-compose logs -f --tail=100
```

## 🔒 Segurança

### Verificação de Segurança
```bash
# Verificar dependências
make security-check

# Análise de código
python -m bandit -r .
```

### Backup e Restore
```bash
# Backup automático
make auto-backup

# Backup manual
make backup
make backup-db

# Restore
make restore BACKUP_FILE=backup.json
make restore-db DB_FILE=backup.sqlite3
```

## 🚀 Deploy em Produção

### 1. Preparação
```bash
# Configurar ambiente de produção
make env-prod

# Verificar pré-requisitos
make check
```

### 2. Deploy
```bash
# Deploy completo
make prod-setup

# Ou usando script
./deploy.sh --env production
```

### 3. Verificação
```bash
# Verificar saúde
make health

# Verificar logs
make logs

# Monitorar recursos
make monitor
```

## 🔄 CI/CD

### Pipeline CI
```bash
make ci  # check + install + test
```

### Pipeline CD
```bash
make cd  # check + deploy + health
```

## 🛠️ Troubleshooting

### Problemas Comuns

1. **Docker não encontrado**
   ```bash
   # Instalar Docker
   curl -fsSL https://get.docker.com | sh
   ```

2. **Porta 8000 ocupada**
   ```bash
   # Parar containers
   make stop
   
   # Ou mudar porta
   docker-compose up -p 8001:8000
   ```

3. **Erro de permissão**
   ```bash
   # Dar permissão aos scripts
   chmod +x deploy.sh
   ```

4. **Módulos não inicializados**
   ```bash
   # Reinicializar módulos
   python manage.py shell -c "
   from apps.config.models.app_module_config import AppModuleConfiguration
   AppModuleConfiguration.initialize_core_modules()
   "
   ```

### Modo Debug
```bash
# Ativar modo debug
make debug

# Verificar problemas
make fix
```

## 📈 Performance

### Otimizações
- Compressão de arquivos estáticos
- Cache Redis
- Otimização de imagens
- Lazy loading

### Monitoramento
```bash
# Análise de performance
make profile

# Monitorar recursos
make monitor
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/fireflies/issues)
- **Documentação**: [Wiki](https://github.com/seu-usuario/fireflies/wiki)
- **Email**: suporte@fireflies.com

## 🎯 Roadmap

- [ ] Integração com Kubernetes
- [ ] Deploy automático via GitHub Actions
- [ ] Sistema de notificações
- [ ] Dashboard de monitoramento
- [ ] Backup automático para cloud
- [ ] Sistema de plugins

---

**FireFlies** - Deploy automatizado com a elegância dos vaga-lumes ✨

## 🏗️ Arquitetura SOLID e Injeção de Dependências

### ServiceFactory (Injeção Automática)

Utilize o ServiceFactory para obter instâncias de serviços já com dependências injetadas:

```python
from core.factories import service_factory

# Obter um serviço já com dependências injetadas
article_service = service_factory.create_article_service()
profile_service = service_factory.create_profile_service()
```

### Observer/Dispatcher de Eventos

Implemente lógica reativa desacoplada usando o padrão Observer:

```python
from core.observers import event_dispatcher

def on_article_created(article):
    print(f"Novo artigo criado: {article.title}")

# Inscrever função para evento
event_dispatcher.subscribe('article_created', on_article_created)

# Disparar evento em algum ponto do código
# (ex: após salvar um artigo)
event_dispatcher.notify('article_created', article_instance)
```

---

# FireFlies CMS

Sistema de gerenciamento de conteúdo modular, seguro e moderno, com wizard de configuração inicial.

## 🚀 Instalação e Setup

### 1. Instale as dependências
```bash
pip install -r requirements.txt
```

### 2. Execute as migrações
```bash
python manage.py migrate
```

### 3. Inicie o servidor
```bash
python manage.py runserver
```

### 4. Wizard de Configuração
Ao acessar o sistema pela primeira vez, você será redirecionado para o wizard de configuração inicial, onde poderá:
- Configurar o banco de dados
- Criar o usuário administrador
- Configurar email
- Definir opções de segurança

## 🧙‍♂️ Wizard de Configuração
O wizard pode ser acessado manualmente em `/config/setup/` se o arquivo `.first_install` existir na raiz do projeto.

## 🧪 Testes
```bash
python manage.py test
```

## 🛡️ Segurança
- Proteção CSRF
- Validação de dados
- Configuração de email segura

## 📚 Documentação
- O código segue padrões SOLID e arquitetura modular.
- Veja a pasta `docs/` para guias de arquitetura e padrões.
