# Arquitetura FireFlies CMS

## Decisões Arquiteturais
- Separação por apps Django (accounts, articles, config, pages).
- Uso de padrões Service, Repository, Interface.
- Templates DRY com includes centralizados.
- Suporte a temas claro/escuro via CSS customizado.

## Fluxos Principais
- Autenticação e registro de usuários.
- CRUD de artigos, comentários e páginas.
- Painel administrativo para configuração de módulos, usuários e permissões.

## Padrões e Boas Práticas
- Signals para ações automáticas (ex: pós-registro).
- Testes unitários e de integração.
- Uso de variáveis de ambiente para configuração.

## Integração
- Integração entre apps via signals, serviços e repositórios.
- Painel admin centraliza permissões e módulos. 