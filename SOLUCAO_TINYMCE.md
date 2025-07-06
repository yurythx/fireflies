# 🚀 Solução Rápida - TinyMCE não aparece em Produção

## ❌ Problema
O editor TinyMCE não aparece no formulário de criação de artigos em produção.

## 🔍 Diagnóstico
- TinyMCE não está sendo carregado corretamente
- Arquivos estáticos não foram coletados
- Scripts do TinyMCE não estão incluídos no template

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
python manage.py fix_tinymce
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
python fix_tinymce_production.py
```

### **Opção 3: Correção Manual (Se as opções acima falharem)**

```bash
# 1. Acesse o servidor de produção
ssh seu-usuario@34.82.179.160

# 2. Navegue para o diretório do projeto
cd /var/www/fireflies

# 3. Ative o ambiente virtual
source env/bin/activate

# 4. Baixar TinyMCE manualmente
wget https://download.tiny.cloud/tinymce/community/tinymce_6.8.3.zip
unzip tinymce_6.8.3.zip
mv tinymce staticfiles/tinymce
rm tinymce_6.8.3.zip

# 5. Coletar arquivos estáticos
python manage.py collectstatic --noinput --clear

# 6. Reiniciar serviços
sudo systemctl restart fireflies
```

## 🔧 Verificação

Após aplicar a correção, verifique se funcionou:

```bash
# Verificar se os arquivos existem
ls -la staticfiles/tinymce/tinymce.min.js
ls -la staticfiles/js/tinymce-init.js
ls -la staticfiles/css/tinymce-content.css

# Verificar se o template foi atualizado
grep -n "tinymce.min.js" apps/pages/templates/base.html

# Testar se a aplicação está funcionando
curl -I http://34.82.179.160/artigos/criar/
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
curl -I http://34.82.179.160/static/tinymce/tinymce.min.js
```

## 🛡️ Prevenção

Para evitar problemas futuros:

### **1. Adicionar ao script de deploy**

```bash
# Sempre executar correção do TinyMCE antes do deploy
python manage.py fix_tinymce

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### **2. Verificação periódica**

```bash
# Adicionar ao crontab para verificar diariamente
0 2 * * * cd /var/www/fireflies && source env/bin/activate && python manage.py fix_tinymce --download-only
```

### **3. Backup dos arquivos**

```bash
# Backup dos arquivos do TinyMCE
cp -r staticfiles/tinymce staticfiles/tinymce.backup.$(date +%Y%m%d_%H%M%S)
```

## 🆘 Se nada funcionar

### **1. Verificar permissões**
```bash
# Verificar permissões dos arquivos estáticos
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/
```

### **2. Verificar configuração do servidor web**
```bash
# Verificar configuração do Nginx/Apache
sudo nginx -t
sudo systemctl status nginx
```

### **3. Verificar logs de erro**
```bash
# Logs do Django
tail -f /var/log/fireflies.log

# Logs do servidor web
sudo tail -f /var/log/nginx/error.log
```

### **4. Contatar suporte**
- Verificar logs completos
- Documentar passos executados
- Fornecer output dos comandos

## 📋 Checklist de Solução

- [ ] Identificar o problema (TinyMCE não aparece)
- [ ] Escolher método de correção
- [ ] Executar correção
- [ ] Verificar se funcionou
- [ ] Reiniciar serviços
- [ ] Testar aplicação
- [ ] Documentar solução
- [ ] Implementar prevenção

## 🎯 Resultado Esperado

Após a correção:
- ✅ `/artigos/criar/` deve mostrar o editor TinyMCE
- ✅ Arquivos do TinyMCE devem estar em `staticfiles/tinymce/`
- ✅ Scripts devem estar incluídos no template
- ✅ Editor deve ter todas as ferramentas (negrito, itálico, etc.)

## 🔍 Debugging

Se o problema persistir, verifique:

### **1. Console do navegador**
```javascript
// Abra o console (F12) e verifique:
console.log(typeof tinymce); // Deve retornar "function"
console.log(window.tinyMCEInitialized); // Deve retornar true
```

### **2. Network tab**
- Verifique se `tinymce.min.js` está sendo carregado
- Verifique se `tinymce-init.js` está sendo carregado
- Verifique se `tinymce-content.css` está sendo carregado

### **3. Elementos HTML**
- Verifique se o textarea tem a classe `tinymce`
- Verifique se os scripts estão no `<head>` do HTML

---

**⏱️ Tempo estimado**: 10-15 minutos  
**🛠️ Complexidade**: Média  
**⚠️ Risco**: Baixo  
**📞 Suporte**: Se precisar de ajuda, forneça os logs de erro 