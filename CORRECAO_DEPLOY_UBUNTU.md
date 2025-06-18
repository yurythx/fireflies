# 🔧 Correção dos Problemas do Deploy Ubuntu

## Problemas Identificados

Baseado no log do deploy, foram identificados os seguintes problemas:

1. **❌ Docker Compose não encontrado**
2. **❌ Usuário não está no grupo docker**
3. **❌ Arquivo .env não encontrado**
4. **❌ Erro de sintaxe no docker-compose.yml**
5. **⚠️ Porta 80 ocupada**

## 🚀 Solução Rápida

### Passo 1: Executar Script de Correção

```bash
# No servidor Ubuntu (skynet)
cd /home/suporte/fireflies

# Dar permissão de execução
chmod +x fix_deploy_issues.sh

# Executar correção automática
./fix_deploy_issues.sh
```

### Passo 2: Ativar Grupo Docker

```bash
# Após executar o script, ativar o grupo docker
newgrp docker
```

### Passo 3: Verificar Correções

```bash
# Verificar se tudo está funcionando
./deploy_improved.sh --check-only
```

### Passo 4: Executar Deploy

```bash
# Se tudo estiver OK, executar o deploy
./deploy_improved.sh
```

## 🔧 Correção Manual (Alternativa)

Se preferir corrigir manualmente:

### 1. Instalar Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Adicionar Usuário ao Grupo Docker

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Criar Arquivo .env

```bash
# Criar arquivo .env com configurações básicas
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=django-insecure-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100
DB_NAME=fireflies_prod
DB_USER=fireflies_user
DB_PASSWORD=fireflies_password
DB_HOST=db
DB_PORT=5432
EOF
```

### 4. Verificar Docker Compose

```bash
# Validar sintaxe do docker-compose.yml
docker-compose config
```

### 5. Criar Diretórios

```bash
mkdir -p logs staticfiles media
```

## 📋 Verificações Pós-Correção

### Verificar Docker Compose
```bash
docker-compose --version
```

### Verificar Grupo Docker
```bash
groups
# Deve mostrar "docker" na lista
```

### Verificar Arquivo .env
```bash
ls -la .env
cat .env
```

### Verificar Portas
```bash
# Verificar se porta 80 está ocupada
sudo netstat -tulpn | grep :80

# Se estiver ocupada, identificar o processo
sudo lsof -i :80
```

## 🚨 Solução para Porta 80 Ocupada

Se a porta 80 estiver ocupada:

### Opção 1: Parar Serviço Conflitante
```bash
# Identificar processo usando porta 80
sudo lsof -i :80

# Parar o serviço (exemplo: nginx)
sudo systemctl stop nginx
```

### Opção 2: Usar Porta Alternativa
```bash
# Editar docker-compose.yml para usar porta 8080
# Alterar linha: "80:80" para "8080:80"
```

## 🔍 Comandos de Diagnóstico

### Verificar Status do Sistema
```bash
# Informações do sistema
uname -a
free -h
df -h

# Status do Docker
docker --version
docker-compose --version
docker info

# Status das portas
sudo netstat -tulpn | grep -E ':(80|8000|5432|6379)'
```

### Verificar Logs
```bash
# Logs do deploy
./deploy_improved.sh --logs

# Logs do Docker
docker-compose logs

# Logs específicos
docker-compose logs web
docker-compose logs db
```

## ✅ Checklist de Verificação

- [ ] Docker Compose instalado e funcionando
- [ ] Usuário no grupo docker
- [ ] Arquivo .env criado
- [ ] docker-compose.yml válido
- [ ] Portas disponíveis
- [ ] Diretórios criados
- [ ] Permissões configuradas

## 🆘 Troubleshooting

### Se Docker Compose não funcionar:
```bash
# Reinstalar Docker Compose
sudo rm /usr/local/bin/docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Se usuário não conseguir usar Docker:
```bash
# Reiniciar serviço Docker
sudo systemctl restart docker

# Verificar status
sudo systemctl status docker
```

### Se arquivo .env não for criado:
```bash
# Criar manualmente
touch .env
nano .env
# Adicionar configurações básicas
```

## 📞 Suporte

Se os problemas persistirem, execute:

```bash
# Coletar informações de diagnóstico
./deploy_improved.sh --diagnose

# Verificar saúde do sistema
./deploy_improved.sh --health
```

---

**Nota:** Execute os comandos como root ou com sudo quando necessário. O script `fix_deploy_issues.sh` automatiza todas essas correções. 