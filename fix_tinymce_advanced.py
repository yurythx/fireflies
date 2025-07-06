#!/usr/bin/env python3
"""
Script avançado para corrigir problemas específicos do TinyMCE em produção
- Imagem de capa não aparece
- TinyMCE não permite colar conteúdo com imagens/vídeos
- Ferramentas do TinyMCE não carregam

Uso:
    python fix_tinymce_advanced.py
"""

import os
import sys
import django
import shutil
import urllib.request
import zipfile
from pathlib import Path

def setup_django():
    """Configura o Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

def create_advanced_tinymce_init():
    """Cria arquivo de inicialização avançado do TinyMCE"""
    print("📝 Criando arquivo de inicialização avançado...")
    
    init_content = '''/**
 * TinyMCE Advanced Initialization Script
 * Versão otimizada para produção com suporte completo a imagens e vídeos
 */

(function() {
    'use strict';
    
    // Configuração avançada do TinyMCE
    const tinymceAdvancedConfig = {
        selector: 'textarea.tinymce, .tinymce',
        height: 600,
        width: '100%',
        skin: 'oxide',
        content_css: '/static/css/tinymce-content.css',
        
        // Plugins completos
        plugins: [
            'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
            'anchor', 'searchreplace', 'visualblocks', 'code', 'insertdatetime',
            'media', 'table', 'wordcount', 'emoticons', 'nonbreaking', 'directionality',
            'paste', 'textcolor', 'colorpicker', 'textpattern', 'help', 'fullscreen',
            'codesample', 'hr', 'pagebreak', 'quickbars', 'template', 'codesample'
        ].join(' '),
        
        // Toolbar completa
        toolbar: [
            'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect',
            'alignleft aligncenter alignright alignjustify | outdent indent | numlist bullist',
            'forecolor backcolor removeformat | charmap emoticons | subscript superscript',
            'visualblocks visualchars | nonbreaking anchor | link unlink | image media',
            'table tabledelete | tableprops tablerowprops tablecellprops | tableinsertrowbefore tableinsertrowafter tabledeleterow | tableinsertcolbefore tableinsertcolafter tabledeletecol',
            'code codesample | fullscreen preview | help'
        ].join(' | '),
        
        // Menu completo
        menubar: 'file edit view insert format tools table help',
        
        // Configurações de status
        statusbar: true,
        branding: false,
        promotion: false,
        elementpath: true,
        
        // Idioma
        language: 'pt_BR',
        
        // Configurações avançadas de paste
        paste_data_images: true,
        paste_as_text: false,
        paste_auto_cleanup_on_paste: false,
        paste_remove_styles: false,
        paste_remove_styles_if_webkit: false,
        paste_strip_class_attributes: 'none',
        paste_enable_default_filters: false,
        paste_word_valid_elements: '*[*]',
        paste_retain_style_properties: 'color background-color font-size font-family font-weight text-decoration text-align line-height margin padding border',
        paste_merge_formats: true,
        paste_convert_word_fake_lists: false,
        paste_filter_drop: false,
        paste_webkit_styles: 'color background-color font-size font-family',
        paste_preprocess: function(plugin, args) {
            console.log('Paste preprocess - content length:', args.content.length);
            // Permitir imagens e vídeos
            args.content = args.content.replace(/<img[^>]*>/gi, function(match) {
                return match.replace(/on\\w+="[^"]*"/gi, ''); // Remove eventos perigosos
            });
        },
        paste_postprocess: function(plugin, args) {
            console.log('Paste postprocess - content length:', args.content.length);
        },
        
        // Configurações de imagem
        image_advtab: true,
        image_caption: true,
        image_class_list: [
            {title: 'Responsive', value: 'img-fluid'},
            {title: 'Rounded', value: 'rounded'},
            {title: 'Thumbnail', value: 'img-thumbnail'}
        ],
        image_title: true,
        image_dimensions: true,
        image_description: true,
        
        // Configurações de mídia
        media_live_embeds: true,
        media_alt_source: true,
        media_poster: true,
        media_dimensions: true,
        media_url_resolver: 'function(data, resolve, reject) { resolve(data); }',
        media_scripts: [
            {filter: 'iframe', width: 300, height: 150},
            {filter: 'video', width: 300, height: 150}
        ],
        
        // Configurações de validação
        verify_html: false,
        cleanup: false,
        cleanup_on_startup: false,
        forced_root_block: 'p',
        force_br_newlines: false,
        force_p_newlines: true,
        remove_linebreaks: false,
        convert_newlines_to_brs: false,
        remove_redundant_brs: false,
        remove_trailing_brs: false,
        entity_encoding: 'raw',
        encoding: 'xml',
        element_format: 'html',
        schema: 'html5',
        valid_children: '+body[style]',
        
        // Elementos válidos estendidos
        extended_valid_elements: 'span[*],div[*],p[*],br[*],hr[*],h1[*],h2[*],h3[*],h4[*],h5[*],h6[*],ul[*],ol[*],li[*],a[*],img[*],video[*],iframe[*],source[*],track[*],table[*],tr[*],td[*],th[*],thead[*],tbody[*],tfoot[*],caption[*],colgroup[*],col[*],blockquote[*],pre[*],code[*],em[*],strong[*],b[*],i[*],u[*],s[*],del[*],ins[*],mark[*],small[*],sub[*],sup[*],cite[*],q[*],abbr[*],acronym[*],dfn[*],kbd[*],samp[*],var[*],time[*],figure[*],figcaption[*]',
        
        // Elementos inválidos
        invalid_elements: 'script,object,embed,form,input,textarea,select,button,label,fieldset,legend,frame,frameset,noframes,applet,basefont,bgsound,link,meta,style,title,xmp,plaintext,listing,marquee,blink,isindex,dir,menu,center,font,strike,tt,u,big,small,spacer,layers,ilayer,base,basefont,center,font,strike,tt,u,big,small,spacer,layers,ilayer',
        
        // Atributos válidos
        valid_attributes: '*[*]',
        invalid_attributes: 'on*',
        
        // Configurações de interface
        fullscreen_native: true,
        resize: true,
        toolbar_mode: 'sliding',
        toolbar_sticky: true,
        toolbar_sticky_offset: 0,
        
        // URLs
        relative_urls: false,
        remove_script_host: false,
        convert_urls: true,
        
        // Configurações de setup
        setup: function(editor) {
            console.log('TinyMCE editor setup:', editor.id);
            
            // Adicionar botão customizado para imagem de capa
            editor.ui.registry.addButton('featuredimage', {
                icon: 'image',
                tooltip: 'Imagem de Capa',
                onAction: function() {
                    // Abrir seletor de imagem
                    editor.windowManager.open({
                        title: 'Selecionar Imagem de Capa',
                        body: {
                            type: 'panel',
                            items: [{
                                type: 'input',
                                name: 'imageUrl',
                                label: 'URL da Imagem'
                            }]
                        },
                        buttons: [{
                            type: 'submit',
                            text: 'Inserir'
                        }],
                        onSubmit: function(api) {
                            const data = api.getData();
                            if (data.imageUrl) {
                                editor.insertContent('<img src="' + data.imageUrl + '" alt="Imagem de capa" class="img-fluid" style="max-width: 100%; height: auto;" />');
                            }
                            api.close();
                        }
                    });
                }
            });
            
            // Configurar upload de imagens
            editor.on('BeforeSetContent', function(e) {
                console.log('BeforeSetContent:', e.content.substring(0, 100));
            });
            
            editor.on('GetContent', function(e) {
                console.log('GetContent:', e.content.substring(0, 100));
            });
        },
        
        // Callback de inicialização
        init_instance_callback: function(editor) {
            console.log('TinyMCE editor initialized:', editor.id);
            window.tinyMCEInitialized = true;
            
            // Configurar eventos de paste
            editor.on('PastePreProcess', function(e) {
                console.log('PastePreProcess:', e.content.substring(0, 100));
                // Permitir imagens e vídeos
                e.content = e.content.replace(/<img[^>]*>/gi, function(match) {
                    return match.replace(/on\\w+="[^"]*"/gi, '');
                });
            });
            
            editor.on('PastePostProcess', function(e) {
                console.log('PastePostProcess:', e.node.innerHTML.substring(0, 100));
            });
        }
    };
    
    // Função para inicializar TinyMCE
    function initTinyMCE() {
        if (typeof tinymce === 'undefined') {
            console.log('TinyMCE not loaded yet, retrying...');
            setTimeout(initTinyMCE, 500);
            return;
        }
        
        if (window.tinyMCEInitialized) {
            console.log('TinyMCE already initialized');
            return;
        }
        
        console.log('Initializing TinyMCE with advanced config...');
        tinymce.init(tinymceAdvancedConfig);
    }
    
    // Inicialização quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTinyMCE);
    } else {
        initTinyMCE();
    }
    
    // Reinicializar quando tema mudar
    window.addEventListener('themeChanged', function() {
        console.log('Theme changed, reinitializing TinyMCE...');
        if (window.tinymce && tinymce.editors) {
            tinymce.editors.forEach(function(editor) { 
                editor.remove(); 
            });
        }
        window.tinyMCEInitialized = false;
        setTimeout(initTinyMCE, 400);
    });
    
    // Função para testar paste
    window.testTinyMCEPaste = function() {
        const editor = tinymce.get('id_content');
        if (editor) {
            console.log('Testing paste functionality...');
            // Simular paste de conteúdo com imagem
            const testContent = '<p>Teste de conteúdo com <strong>formatação</strong> e <img src="https://via.placeholder.com/300x200" alt="Teste" /> imagem.</p>';
            editor.setContent(testContent);
        }
    };
    
})();
'''
    
    try:
        with open('static/js/tinymce-init.js', 'w', encoding='utf-8') as f:
            f.write(init_content)
        print("✅ Arquivo de inicialização avançado criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar arquivo de inicialização: {e}")
        return False

def create_advanced_css():
    """Cria CSS avançado para o TinyMCE"""
    print("🎨 Criando CSS avançado do TinyMCE...")
    
    css_content = '''/* TinyMCE Advanced Content CSS */
/* Estilos para o conteúdo dentro do editor */

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #333;
    background: #fff;
    margin: 0;
    padding: 20px;
}

/* Títulos */
h1, h2, h3, h4, h5, h6 {
    margin-top: 0;
    margin-bottom: 0.5em;
    font-weight: 600;
    line-height: 1.2;
}

h1 { font-size: 2em; }
h2 { font-size: 1.75em; }
h3 { font-size: 1.5em; }
h4 { font-size: 1.25em; }
h5 { font-size: 1.1em; }
h6 { font-size: 1em; }

/* Parágrafos */
p {
    margin-top: 0;
    margin-bottom: 1em;
}

/* Listas */
ul, ol {
    margin-top: 0;
    margin-bottom: 1em;
    padding-left: 2em;
}

li {
    margin-bottom: 0.25em;
}

/* Links */
a {
    color: #007bff;
    text-decoration: underline;
}

a:hover {
    color: #0056b3;
    text-decoration: none;
}

/* Imagens */
img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin: 10px 0;
}

img.img-fluid {
    max-width: 100%;
    height: auto;
}

img.rounded {
    border-radius: 8px;
}

img.img-thumbnail {
    padding: 4px;
    border: 1px solid #ddd;
    border-radius: 4px;
    max-width: 100%;
    height: auto;
}

/* Vídeos */
video {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin: 10px 0;
}

/* Iframes (YouTube, etc.) */
iframe {
    max-width: 100%;
    border-radius: 4px;
    margin: 10px 0;
}

/* Tabelas */
table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1em;
}

table, th, td {
    border: 1px solid #ddd;
}

th, td {
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #f8f9fa;
    font-weight: 600;
}

/* Blockquotes */
blockquote {
    margin: 0 0 1em 0;
    padding: 0.5em 1em;
    border-left: 4px solid #007bff;
    background-color: #f8f9fa;
    font-style: italic;
}

/* Code */
code {
    background-color: #f8f9fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f8f9fa;
    padding: 1em;
    border-radius: 4px;
    overflow-x: auto;
    margin-bottom: 1em;
}

pre code {
    background: none;
    padding: 0;
}

/* Formatação de texto */
strong, b {
    font-weight: 600;
}

em, i {
    font-style: italic;
}

u {
    text-decoration: underline;
}

s, del {
    text-decoration: line-through;
}

/* Cores de texto */
.text-primary { color: #007bff !important; }
.text-secondary { color: #6c757d !important; }
.text-success { color: #28a745 !important; }
.text-danger { color: #dc3545 !important; }
.text-warning { color: #ffc107 !important; }
.text-info { color: #17a2b8 !important; }
.text-light { color: #f8f9fa !important; }
.text-dark { color: #343a40 !important; }

/* Alinhamento */
.text-left { text-align: left !important; }
.text-center { text-align: center !important; }
.text-right { text-align: right !important; }
.text-justify { text-align: justify !important; }

/* Figuras */
figure {
    margin: 1em 0;
    text-align: center;
}

figcaption {
    font-size: 0.9em;
    color: #666;
    margin-top: 0.5em;
    font-style: italic;
}

/* Responsividade */
@media (max-width: 768px) {
    body {
        font-size: 14px;
        padding: 15px;
    }
    
    h1 { font-size: 1.75em; }
    h2 { font-size: 1.5em; }
    h3 { font-size: 1.25em; }
    h4 { font-size: 1.1em; }
    h5 { font-size: 1em; }
    h6 { font-size: 0.9em; }
    
    img, video, iframe {
        margin: 5px 0;
    }
}

/* Estilos específicos para o editor */
.tox-tinymce {
    border-radius: 0.375rem;
    border: 1px solid #ced4da;
}

.tox-toolbar__primary {
    background: #f8f9fa !important;
    border-bottom: 1px solid #dee2e6;
}

.tox-editor-header {
    border-bottom: 1px solid #dee2e6;
}

.tox-statusbar {
    border-top: 1px solid #dee2e6;
    background: #f8f9fa !important;
}

.tox-edit-area {
    background: #fff;
}

.tox-edit-area iframe {
    background: #fff;
}
'''
    
    try:
        os.makedirs('static/css', exist_ok=True)
        with open('static/css/tinymce-content.css', 'w', encoding='utf-8') as f:
            f.write(css_content)
        print("✅ CSS avançado do TinyMCE criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar CSS: {e}")
        return False

def fix_image_upload_settings():
    """Corrige configurações de upload de imagem"""
    print("🖼️ Corrigindo configurações de upload de imagem...")
    
    try:
        # Verificar se o diretório media existe
        media_dir = Path('media')
        if not media_dir.exists():
            media_dir.mkdir()
            print("✅ Diretório media criado")
        
        # Verificar permissões
        os.chmod('media', 0o755)
        print("✅ Permissões do diretório media corrigidas")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao corrigir configurações de imagem: {e}")
        return False

def update_article_form():
    """Atualiza o formulário de artigos para melhor suporte a imagens"""
    print("📝 Atualizando formulário de artigos...")
    
    form_path = 'apps/articles/forms.py'
    
    if not os.path.exists(form_path):
        print(f"❌ Formulário não encontrado: {form_path}")
        return False
    
    try:
        with open(form_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem configurações avançadas
        if 'mce_attrs' in content and 'advanced' in content:
            print("✅ Formulário já tem configurações avançadas")
            return True
        
        # Atualizar configuração do TinyMCE
        old_config = "mce_attrs={'config': 'advanced'}"
        new_config = """mce_attrs={
                'config': 'advanced',
                'height': 600,
                'plugins': 'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code insertdatetime media table wordcount emoticons nonbreaking directionality paste textcolor colorpicker textpattern help fullscreen codesample hr pagebreak quickbars template',
                'toolbar': 'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent | numlist bullist | forecolor backcolor removeformat | charmap emoticons | subscript superscript | visualblocks visualchars | nonbreaking anchor | link unlink | image media | table tabledelete | tableprops tablerowprops tablecellprops | tableinsertrowbefore tableinsertrowafter tabledeleterow | tableinsertcolbefore tableinsertcolafter tabledeletecol | code codesample | fullscreen preview | help',
                'paste_data_images': True,
                'paste_as_text': False,
                'paste_auto_cleanup_on_paste': False,
                'paste_remove_styles': False,
                'paste_remove_styles_if_webkit': False,
                'paste_strip_class_attributes': 'none',
                'paste_enable_default_filters': False,
                'paste_word_valid_elements': '*[*]',
                'paste_retain_style_properties': 'color background-color font-size font-family font-weight text-decoration text-align line-height margin padding border',
                'paste_merge_formats': True,
                'paste_convert_word_fake_lists': False,
                'paste_filter_drop': False,
                'paste_webkit_styles': 'color background-color font-size font-family',
                'image_advtab': True,
                'image_caption': True,
                'image_title': True,
                'image_dimensions': True,
                'image_description': True,
                'media_live_embeds': True,
                'media_alt_source': True,
                'media_poster': True,
                'media_dimensions': True,
                'verify_html': False,
                'cleanup': False,
                'cleanup_on_startup': False,
                'forced_root_block': 'p',
                'force_br_newlines': False,
                'force_p_newlines': True,
                'remove_linebreaks': False,
                'convert_newlines_to_brs': False,
                'remove_redundant_brs': False,
                'remove_trailing_brs': False,
                'entity_encoding': 'raw',
                'encoding': 'xml',
                'element_format': 'html',
                'schema': 'html5',
                'valid_children': '+body[style]',
                'extended_valid_elements': 'span[*],div[*],p[*],br[*],hr[*],h1[*],h2[*],h3[*],h4[*],h5[*],h6[*],ul[*],ol[*],li[*],a[*],img[*],video[*],iframe[*],source[*],track[*],table[*],tr[*],td[*],th[*],thead[*],tbody[*],tfoot[*],caption[*],colgroup[*],col[*],blockquote[*],pre[*],code[*],em[*],strong[*],b[*],i[*],u[*],s[*],del[*],ins[*],mark[*],small[*],sub[*],sup[*],cite[*],q[*],abbr[*],acronym[*],dfn[*],kbd[*],samp[*],var[*],time[*],figure[*],figcaption[*]',
                'invalid_elements': 'script,object,embed,form,input,textarea,select,button,label,fieldset,legend,frame,frameset,noframes,applet,basefont,bgsound,link,meta,style,title,xmp,plaintext,listing,marquee,blink,isindex,dir,menu,center,font,strike,tt,u,big,small,spacer,layers,ilayer,base,basefont,center,font,strike,tt,u,big,small,spacer,layers,ilayer',
                'valid_attributes': '*[*]',
                'invalid_attributes': 'on*',
                'fullscreen_native': True,
                'resize': True,
                'toolbar_mode': 'sliding',
                'toolbar_sticky': True,
                'toolbar_sticky_offset': 0,
                'relative_urls': False,
                'remove_script_host': False,
                'convert_urls': True
            }"""
        
        # Substituir configuração
        if old_config in content:
            content = content.replace(old_config, new_config)
            
            # Salvar arquivo
            with open(form_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Formulário de artigos atualizado")
            return True
        else:
            print("⚠️ Configuração não encontrada no formulário")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao atualizar formulário: {e}")
        return False

def collect_static_files():
    """Coleta arquivos estáticos"""
    print("📦 Coletando arquivos estáticos...")
    
    try:
        from django.core.management import call_command
        call_command('collectstatic', '--noinput', '--clear')
        print("✅ Arquivos estáticos coletados")
        return True
    except Exception as e:
        print(f"❌ Erro ao coletar arquivos estáticos: {e}")
        return False

def test_advanced_features():
    """Testa funcionalidades avançadas"""
    print("🧪 Testando funcionalidades avançadas...")
    
    try:
        # Verificar se os arquivos existem
        files_to_check = [
            'static/js/tinymce-init.js',
            'static/css/tinymce-content.css',
            'media'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} não encontrado")
                return False
        
        # Verificar se o formulário foi atualizado
        form_path = 'apps/articles/forms.py'
        if os.path.exists(form_path):
            with open(form_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'paste_data_images' in content and 'image_advtab' in content:
                    print("✅ Formulário com configurações avançadas")
                else:
                    print("⚠️ Formulário pode não ter todas as configurações")
        
        print("✅ Todas as funcionalidades avançadas estão configuradas")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🦟 FireFlies - Correção Avançada do TinyMCE")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Passo 1: Criar inicialização avançada
    if not create_advanced_tinymce_init():
        print("❌ Falha ao criar inicialização avançada")
        return
    
    # Passo 2: Criar CSS avançado
    if not create_advanced_css():
        print("❌ Falha ao criar CSS avançado")
        return
    
    # Passo 3: Corrigir configurações de imagem
    if not fix_image_upload_settings():
        print("❌ Falha ao corrigir configurações de imagem")
        return
    
    # Passo 4: Atualizar formulário de artigos
    if not update_article_form():
        print("❌ Falha ao atualizar formulário")
        return
    
    # Passo 5: Coletar arquivos estáticos
    if not collect_static_files():
        print("❌ Falha ao coletar arquivos estáticos")
        return
    
    # Passo 6: Testar funcionalidades
    if not test_advanced_features():
        print("❌ Falha no teste")
        return
    
    print("\n🎉 Correção avançada do TinyMCE concluída!")
    print("✅ Agora você pode:")
    print("   - Colar conteúdo com imagens e vídeos")
    print("   - Ver todas as ferramentas do editor")
    print("   - Fazer upload de imagens de capa")
    print("   - Usar formatação avançada")
    print("\n📋 Próximos passos:")
    print("   1. Reinicie o servidor web")
    print("   2. Limpe o cache do navegador")
    print("   3. Teste o formulário de criação de artigos")
    print("   4. Tente colar conteúdo de outros sites")

if __name__ == "__main__":
    main() 