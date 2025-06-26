/**
 * Script de inicialização do TinyMCE
 * Funciona tanto em desenvolvimento quanto em produção
 */

(function() {
    'use strict';
    
    // Função para inicializar TinyMCE
    function initTinyMCE() {
        // Verifica se o TinyMCE já está carregado
        if (typeof tinymce === 'undefined') {
            console.log('TinyMCE Init: TinyMCE not loaded, retrying...');
            setTimeout(initTinyMCE, 1000);
            return;
        }
        
        console.log('TinyMCE Init: Starting initialization...');
        
        // Verifica se já foi inicializado
        if (window.tinyMCEInitialized) {
            console.log('TinyMCE Init: Already initialized');
            return;
        }
        
        // Configuração base
        const baseConfig = {
            selector: 'textarea.tinymce, .tinymce',
            height: 500,
            width: '100%',
            cleanup_on_startup: false,
            custom_undo_redo_levels: 20,
            theme: 'silver',
            plugins: [
                'advlist autolink lists link image charmap preview anchor',
                'searchreplace visualblocks code insertdatetime media',
                'table wordcount emoticons nonbreaking directionality'
            ].join(' '),
            toolbar1: [
                'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect',
                'alignleft aligncenter alignright alignjustify | outdent indent | numlist bullist',
                'forecolor backcolor removeformat | charmap emoticons'
            ].join(' | '),
            toolbar2: [
                'visualblocks visualchars | nonbreaking anchor | link unlink | image media',
                'table | code | customfullscreen | preview | help'
            ].join(' | '),
            menubar: true,
            statusbar: true,
            branding: false,
            promotion: false,
            contextmenu: 'link image table',
            directionality: 'ltr',
            language: 'pt_BR',
            fullscreen_native: true,
            resize: false,
            elementpath: false,
            toolbar_mode: 'sliding',
            toolbar_sticky: true,
            
            // Configurações para preservar formatação
            relative_urls: false,
            remove_script_host: false,
            convert_urls: true,
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
            extended_valid_elements: 'span[*],div[*],p[*],br[*],hr[*],h1[*],h2[*],h3[*],h4[*],h5[*],h6[*],ul[*],ol[*],li[*],a[*],img[*],video[*],iframe[*],table[*],tr[*],td[*],th[*],thead[*],tbody[*],tfoot[*],caption[*],colgroup[*],col[*],blockquote[*],pre[*],code[*],em[*],strong[*],b[*],i[*],u[*],s[*],del[*],ins[*],mark[*],small[*],sub[*],sup[*],cite[*],q[*],abbr[*],acronym[*],dfn[*],kbd[*],samp[*],var[*],time[*]',
            invalid_elements: 'script,object,embed,form,input,textarea,select,button,label,fieldset,legend,frame,frameset,noframes,applet,basefont,bgsound,link,meta,style,title,xmp,plaintext,listing,marquee,blink,isindex,dir,menu,center,font,strike,tt,u,big,small,spacer,layers,ilayer,base,basefont,center,font,strike,tt,u,big,small,spacer,layers,ilayer',
            valid_attributes: '*[*]',
            invalid_attributes: 'on*',
            
            // Configurações para colagem com imagens e vídeos
            paste_data_images: true,
            paste_as_text: false,
            paste_auto_cleanup_on_paste: false,
            paste_remove_styles: false,
            paste_remove_styles_if_webkit: false,
            paste_strip_class_attributes: 'none',
            paste_enable_default_filters: false,
            paste_word_valid_elements: '*[*]',
            paste_retain_style_properties: 'color background-color font-size font-family font-weight text-decoration',
            paste_merge_formats: true,
            paste_convert_word_fake_lists: false,
            paste_filter_drop: false,
            paste_webkit_styles: 'color background-color font-size font-family',
            
            // Configurações de mídia
            media_live_embeds: true,
            media_alt_source: false,
            media_poster: false,
            media_dimensions: false,
            media_url_resolver: function(data, resolve, reject) {
                resolve(data);
            },
            media_scripts: [
                {filter: 'iframe', width: 300, height: 150}
            ],
            
            // CSS personalizado
            content_css: '/static/css/tinymce-content.css',
            
            // Callbacks
            setup: function(editor) {
                console.log('TinyMCE Init: Editor setup complete for', editor.id);
                
                // Força a preservação de formatação na colagem
                editor.on('PastePreProcess', function(e) {
                    console.log('TinyMCE Init: Paste preprocess for', editor.id);
                    // Remove apenas scripts, mantém todo o resto
                    e.content = e.content.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
                });
                
                editor.on('PastePostProcess', function(e) {
                    console.log('TinyMCE Init: Paste postprocess for', editor.id);
                    // Preserva imagens e vídeos
                    if (e.node) {
                        const images = e.node.querySelectorAll('img');
                        const videos = e.node.querySelectorAll('video, iframe');
                        
                        images.forEach(function(img) {
                            if (img.src && img.src.startsWith('data:')) {
                                console.log('TinyMCE Init: Preserving data image in', editor.id);
                            }
                        });
                        
                        videos.forEach(function(video) {
                            console.log('TinyMCE Init: Preserving video/iframe in', editor.id);
                        });
                    }
                });
                
                // Auto-save
                editor.on('KeyUp', function() {
                    if (window.tinyMCEManager && window.tinyMCEManager.autoSaveEnabled) {
                        window.tinyMCEManager.autoSave(editor.id);
                    }
                });
            },
            
            init_instance_callback: function(editor) {
                console.log('TinyMCE Init: Editor initialized for', editor.id);
                window.tinyMCEInitialized = true;
            }
        };
        
        // Inicializa o TinyMCE
        tinymce.init(baseConfig);
    }
    
    // Aguarda o DOM estar pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTinyMCE);
    } else {
        // DOM já está pronto
        initTinyMCE();
    }
    
    // Fallback adicional
    window.addEventListener('load', function() {
        setTimeout(initTinyMCE, 500);
    });
    
})(); 