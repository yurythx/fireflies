/**
 * Script de inicialização do TinyMCE
 * Funciona tanto em desenvolvimento quanto em produção
 */

(function() {
    'use strict';
    
    // Detecta dark mode do site ou sistema
    function isDarkMode() {
        if (document.body && document.body.getAttribute('data-theme') === 'dark') return true;
        if (document.documentElement && document.documentElement.getAttribute('data-theme') === 'dark') return true;
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    // Gera a configuração do TinyMCE conforme o tema
    function getTinyMCEConfig() {
        const darkMode = isDarkMode();
        return {
            selector: 'textarea.tinymce, .tinymce',
            height: 500,
            width: '100%',
            skin: darkMode ? 'oxide-dark' : 'oxide',
            content_css: darkMode ? 'dark' : '/static/css/tinymce-content.css',
            plugins: 'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code insertdatetime media table wordcount emoticons nonbreaking directionality',
            toolbar: 'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent | numlist bullist | forecolor backcolor removeformat | charmap emoticons | visualblocks visualchars | nonbreaking anchor | link unlink | image media | table | code | customfullscreen | preview | help',
            menubar: true,
            statusbar: true,
            branding: false,
            promotion: false,
            language: 'pt_BR',
            // Outras configs e callbacks podem ser adicionadas aqui
            setup: function(editor) {
                // Exemplo: auto-save, paste, etc.
            },
            init_instance_callback: function(editor) {
                window.tinyMCEInitialized = true;
            }
        };
    }

    // Inicializa o TinyMCE
    function initTinyMCE() {
        if (typeof tinymce === 'undefined') {
            setTimeout(initTinyMCE, 500);
            return;
        }
        if (window.tinyMCEInitialized) return;
        tinymce.init(getTinyMCEConfig());
    }

    // Inicialização inicial
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTinyMCE);
    } else {
        initTinyMCE();
    }

    // Reinicializa o TinyMCE ao alternar o tema
    window.addEventListener('themeChanged', function() {
        console.log('Theme changed event received!');
        if (window.tinymce && tinymce.editors) {
            tinymce.editors.forEach(function(editor) { editor.remove(); });
        }
        setTimeout(function() {
            window.tinyMCEInitialized = false;
            if (document.querySelector('textarea.tinymce, .tinymce')) {
                console.log('TinyMCE: Reinicializando após mudança de tema...');
                if (typeof initTinyMCE === 'function') {
                    initTinyMCE();
                }
            } else {
                console.warn('TinyMCE: Nenhum textarea encontrado para reinicializar.');
            }
        }, 400);
    });
})(); 