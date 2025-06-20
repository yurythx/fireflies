# 🚀 Guia do Setup Wizard - FireFlies

## Visão Geral

O FireFlies possui um sistema de configuração inicial (wizard) que permite configurar o banco de dados, criar o usuário administrador, configurar email e opções de segurança na primeira execução do sistema.

## 🎯 Como Funciona

### 1. Primeira Instalação
- O sistema detecta automaticamente se é a primeira instalação (arquivo `.first_install` na raiz).
- Redireciona automaticamente para o wizard de configuração ao acessar o sistema.

### 2. Wizard de Configuração
- **Passo 1**: Configuração do banco de dados (SQLite, PostgreSQL, MySQL)
- **Passo 2**: Criação do usuário administrador
- **Passo 3**: Configuração de email
- **Passo 4**: Opções de segurança
- **Passo 5**: Finalização e aplicação das configurações

### 3. Configuração Automática
- Ao finalizar o wizard, todas as configurações são aplicadas e o arquivo `.first_install` é removido.
- O sistema está pronto para uso.

## 📋 Pré-requisitos

- Python 3.10+
- Instalar dependências:
  ```bash
  pip install -r requirements.txt
  ```
- Executar migrações:
  ```bash
  python manage.py migrate
  ```

## 🧙‍♂️ Como acessar o Wizard

- Inicie o servidor:
  ```bash
  python manage.py runserver
  ```
- Acesse `http://localhost:8000/` no navegador.
- Se for a primeira instalação, você será redirecionado automaticamente para o wizard.
- Caso precise forçar o wizard, crie o arquivo `.first_install` na raiz do projeto:
  ```bash
  touch .first_install
  ```

## 👤 Usuário Administrador
- Nome de usuário único
- Email válido
- Senha mínima de 8 caracteres

## 📧 Configuração de Email
- Console (desenvolvimento): emails aparecem no terminal
- SMTP (produção): configure servidor, porta, usuário e senha

## 🔒 Segurança
- Proteção CSRF
- Validação de dados
- Opções de segurança configuráveis no wizard

## 🐛 Troubleshooting

- Se o wizard não aparecer, verifique se o arquivo `.first_install` existe na raiz do projeto.
- Para forçar o wizard novamente:
  ```bash
  touch .first_install
  ```
- Para remover o modo de primeira instalação:
  ```bash
  rm .first_install
  ```

## 📚 Exemplos de Uso

1. Instale dependências e rode migrações:
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   ```
2. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```
3. Acesse o wizard em `http://localhost:8000/`.
4. Siga os passos do wizard para configurar o sistema.

---

Para dúvidas sobre o wizard, consulte o código em `apps/config/views/setup_wizard_improved.py` ou abra uma issue no repositório. 