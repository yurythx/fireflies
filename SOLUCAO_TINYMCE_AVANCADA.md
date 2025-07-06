# 🚀 Solução Avançada - TinyMCE com Imagens, Vídeos e Ferramentas

## ❌ Problemas Identificados
1. **Imagem de capa não aparece**
2. **TinyMCE não permite colar conteúdo com imagens/vídeos**
3. **Ferramentas do TinyMCE não carregam**

## 🔍 Diagnóstico Detalhado

### **Problema 1: Imagem de Capa**
- Diretório `media` não existe ou sem permissões
- Configurações de upload não definidas
- Formulário não processa imagens corretamente

### **Problema 2: Paste de Conteúdo**
- Configurações de paste muito restritivas
- `paste_data_images: false`
- Elementos inválidos muito restritivos

### **Problema 3: Ferramentas Não Carregam**
- Plugins não incluídos
- Toolbar incompleta
- Configuração básica demais

## ✅ Soluções Específicas

### **Opção 1: Comando Django Avançado (Recomendado)**

```bash
# 1. Acesse o servidor de produção
ssh seu-usuario@34.82.179.160

# 2. Navegue para o diretório do projeto
cd /var/www/fireflies

# 3. Ative o ambiente virtual
source env/bin/activate

# 4. Execute o comando de correção avançada
python manage.py fix_tinymce_advanced
```

### **Opção 2: Script Python Avançado**

```bash
# 1. Acesse o servidor de produção
ssh seu-usuario@34.82.179.160

# 2. Navegue para o diretório do projeto
cd /var/www/fireflies

# 3. Ative o ambiente virtual
source env/bin/activate

# 4. Execute o script de correção avançada
python fix_tinymce_advanced.py
```

### **Opção 3: Correções Específicas**

#### **A. Corrigir Apenas Imagens**
```bash
python manage.py fix_tinymce_advanced --images-only
```

#### **B. Corrigir Apenas Paste**
```bash
python manage.py fix_tinymce_advanced --paste-only
```

## 🔧 O que a Solução Avançada Faz

### **1. Configurações de Imagem**
- ✅ Cria diretório `media` com permissões corretas
- ✅ Configura `paste_data_images: true`
- ✅ Adiciona suporte a `image_advtab`, `image_caption`
- ✅ Permite upload de imagens de capa

### **2. Configurações de Paste**
- ✅ `paste_data_images: true` - Permite colar imagens
- ✅ `paste_as_text: false` - Mantém formatação
- ✅ `paste_auto_cleanup_on_paste: false` - Não limpa conteúdo
- ✅ `paste_remove_styles: false` - Mantém estilos
- ✅ `paste_word_valid_elements: '*[*]'` - Permite todos os elementos
- ✅ `extended_valid_elements` - Inclui vídeos, iframes, etc.

### **3. Ferramentas Completas**
- ✅ **Plugins**: Todos os plugins necessários incluídos
- ✅ **Toolbar**: Toolbar completa com todas as ferramentas
- ✅ **Menu**: Menu completo (File, Edit, View, Insert, etc.)
- ✅ **Elementos**: Suporte a imagens, vídeos, tabelas, etc.

## 🎯 Funcionalidades Habilitadas

### **Paste Avançado**
- ✅ Colar imagens de outros sites
- ✅ Colar vídeos do YouTube
- ✅ Colar conteúdo formatado do Word
- ✅ Colar tabelas complexas
- ✅ Manter formatação original

### **Ferramentas de Edição**
- ✅ **Formatação**: Negrito, itálico, sublinhado, tachado
- ✅ **Alinhamento**: Esquerda, centro, direita, justificado
- ✅ **Listas**: Numeradas e com marcadores
- ✅ **Cores**: Cor do texto e fundo
- ✅ **Links**: Inserir e editar links
- ✅ **Imagens**: Inserir e editar imagens
- ✅ **Mídia**: Inserir vídeos e iframes
- ✅ **Tabelas**: Criar e editar tabelas
- ✅ **Código**: Inserir código e preview
- ✅ **Fullscreen**: Modo tela cheia

### **Upload de Imagens**
- ✅ Imagem de capa funcional
- ✅ Upload de imagens no conteúdo
- ✅ Redimensionamento automático
- ✅ Classes CSS (responsive, rounded, thumbnail)

## 🧪 Testes de Funcionalidade

### **Teste 1: Paste de Conteúdo**
```javascript
// No console do navegador (F12)
// Cole este conteúdo no editor:
<p>Teste com <strong>formatação</strong> e <img src="https://via.placeholder.com/300x200" alt="Teste" /> imagem.</p>
```

### **Teste 2: Upload de Imagem**
1. Vá para `/artigos/criar/`
2. Clique em "Imagem Destacada"
3. Selecione uma imagem
4. Verifique se aparece o preview

### **Teste 3: Ferramentas**
1. Abra o editor
2. Verifique se todas as ferramentas estão visíveis
3. Teste formatação (negrito, itálico, etc.)
4. Teste inserção de imagem e vídeo

## 🛠️ Configurações Técnicas

### **Plugins Habilitados**
```javascript
plugins: [
    'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
    'anchor', 'searchreplace', 'visualblocks', 'code', 'insertdatetime',
    'media', 'table', 'wordcount', 'emoticons', 'nonbreaking', 'directionality',
    'paste', 'textcolor', 'colorpicker', 'textpattern', 'help', 'fullscreen',
    'codesample', 'hr', 'pagebreak', 'quickbars', 'template'
]
```

### **Elementos Válidos**
```javascript
extended_valid_elements: 'span[*],div[*],p[*],br[*],hr[*],h1[*],h2[*],h3[*],h4[*],h5[*],h6[*],ul[*],ol[*],li[*],a[*],img[*],video[*],iframe[*],source[*],track[*],table[*],tr[*],td[*],th[*],thead[*],tbody[*],tfoot[*],caption[*],colgroup[*],col[*],blockquote[*],pre[*],code[*],em[*],strong[*],b[*],i[*],u[*],s[*],del[*],ins[*],mark[*],small[*],sub[*],sup[*],cite[*],q[*],abbr[*],acronym[*],dfn[*],kbd[*],samp[*],var[*],time[*],figure[*],figcaption[*]'
```

### **Configurações de Paste**
```javascript
paste_data_images: true,
paste_as_text: false,
paste_auto_cleanup_on_paste: false,
paste_remove_styles: false,
paste_remove_styles_if_webkit: false,
paste_strip_class_attributes: 'none',
paste_enable_default_filters: false,
paste_word_valid_elements: '*[*]',
paste_retain_style_properties: 'color background-color font-size font-family font-weight text-decoration text-align line-height margin padding border'
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
curl -I http://34.82.179.160/artigos/criar/

# Verificar arquivos estáticos
curl -I http://34.82.179.160/static/js/tinymce-init.js
curl -I http://34.82.179.160/static/css/tinymce-content.css
```

## 🛡️ Prevenção

Para evitar problemas futuros:

### **1. Adicionar ao script de deploy**
```bash
# Sempre executar correção avançada antes do deploy
python manage.py fix_tinymce_advanced
python manage.py collectstatic --noinput
```

### **2. Verificação periódica**
```bash
# Adicionar ao crontab para verificar diariamente
0 2 * * * cd /var/www/fireflies && source env/bin/activate && python manage.py fix_tinymce_advanced --images-only
```

### **3. Backup das configurações**
```bash
# Backup das configurações do TinyMCE
cp static/js/tinymce-init.js static/js/tinymce-init.js.backup.$(date +%Y%m%d_%H%M%S)
cp static/css/tinymce-content.css static/css/tinymce-content.css.backup.$(date +%Y%m%d_%H%M%S)
```

## 🆘 Se nada funcionar

### **1. Verificar permissões**
```bash
# Verificar permissões dos arquivos estáticos
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

# Verificar permissões do diretório media
sudo chown -R www-data:www-data media/
sudo chmod -R 755 media/
```

### **2. Verificar configuração do servidor web**
```bash
# Verificar configuração do Nginx/Apache
sudo nginx -t
sudo systemctl status nginx

# Verificar se está servindo arquivos estáticos
curl -I http://34.82.179.160/static/tinymce/tinymce.min.js
```

### **3. Verificar logs de erro**
```bash
# Logs do Django
tail -f /var/log/fireflies.log

# Logs do servidor web
sudo tail -f /var/log/nginx/error.log

# Logs do sistema
sudo journalctl -u fireflies -f
```

## 📋 Checklist de Solução Avançada

- [ ] Identificar problemas específicos
- [ ] Executar correção avançada
- [ ] Verificar upload de imagens
- [ ] Testar paste de conteúdo
- [ ] Verificar todas as ferramentas
- [ ] Reiniciar serviços
- [ ] Testar funcionalidades
- [ ] Documentar solução
- [ ] Implementar prevenção

## 🎯 Resultado Esperado

Após a correção avançada:
- ✅ **Imagem de capa**: Funciona corretamente
- ✅ **Paste de conteúdo**: Aceita imagens e vídeos
- ✅ **Ferramentas**: Todas as ferramentas disponíveis
- ✅ **Formatação**: Negrito, itálico, cores, etc.
- ✅ **Mídia**: Imagens, vídeos, iframes
- ✅ **Tabelas**: Criação e edição de tabelas
- ✅ **Responsivo**: Funciona em dispositivos móveis

## 🔍 Debugging Avançado

Se o problema persistir, verifique:

### **1. Console do navegador**
```javascript
// Abra o console (F12) e verifique:
console.log(typeof tinymce); // Deve retornar "function"
console.log(window.tinyMCEInitialized); // Deve retornar true
console.log(tinymce.editors.length); // Deve retornar > 0
```

### **2. Network tab**
- Verifique se todos os arquivos estão sendo carregados
- Verifique se não há erros 404 ou 500
- Verifique se os arquivos têm o tamanho correto

### **3. Elementos HTML**
- Verifique se o textarea tem a classe `tinymce`
- Verifique se os scripts estão no `<head>` do HTML
- Verifique se não há conflitos de CSS

---

**⏱️ Tempo estimado**: 15-20 minutos  
**🛠️ Complexidade**: Alta  
**⚠️ Risco**: Baixo  
**📞 Suporte**: Se precisar de ajuda, forneça os logs de erro e screenshots 