/**
 * TinyMCE Manager - Versão Limpa e Otimizada
 * Apenas funcionalidades essenciais: Fullscreen customizado e Auto-save
 */

class TinyMCEManager {
    constructor() {
        this.editors = new Map();
        this.autoSaveEnabled = false;
        this.init();
    }

    init() {
        this.waitForTinyMCE(() => {
            this.setupEventListeners();
        });
    }

    waitForTinyMCE(callback) {
        console.log('TinyMCE Config: Checking if TinyMCE is available...');
        
        if (typeof tinymce !== 'undefined') {
            console.log('TinyMCE Config: TinyMCE found, waiting for full initialization...');
            setTimeout(() => {
                console.log('TinyMCE Config: TinyMCE should be ready now');
                callback();
            }, 1000);
        } else {
            console.log('TinyMCE Config: TinyMCE not found yet, retrying...');
            setTimeout(() => this.waitForTinyMCE(callback), 200);
        }
    }

    setupEventListeners() {
        // Escutar quando editores são adicionados
        tinymce.on('AddEditor', (e) => {
            const editor = e.editor;
            this.editors.set(editor.id, editor);
            this.setupEditorEvents(editor);
        });

        // Escutar quando editores são removidos
        tinymce.on('RemoveEditor', (e) => {
            const editor = e.editor;
            this.editors.delete(editor.id);
        });
        
        // Listener para ESC key
        this.setupEscapeListener();
    }

    setupEditorEvents(editor) {
        // Evento quando o editor está pronto
        editor.on('init', () => {
            console.log(`TinyMCE editor ${editor.id} initialized`);
            this.addCustomFullscreenButton(editor);
        });

        // Evento de mudança de conteúdo para auto-save
        editor.on('change', () => {
            this.handleContentChange(editor);
        });
    }
    
    addCustomFullscreenButton(editor) {
        // Adicionar botão customizado de fullscreen
        editor.ui.registry.addButton('customfullscreen', {
            icon: 'fullscreen',
            tooltip: 'Tela Cheia',
            onAction: () => {
                this.toggleCustomFullscreen(editor);
            }
        });
        
        console.log('Custom fullscreen button added');
    }
    
    toggleCustomFullscreen(editor) {
        const container = editor.getContainer();
        const isFullscreen = container.classList.contains('tox-fullscreen-custom');
        
        if (!isFullscreen) {
            this.enterCustomFullscreen(editor);
        } else {
            this.exitCustomFullscreen(editor);
        }
    }
    
    enterCustomFullscreen(editor) {
        console.log('Entering custom fullscreen');
        
        const container = editor.getContainer();
        const body = document.body;
        
        // Adicionar classes
        container.classList.add('tox-fullscreen-custom');
        body.classList.add('tox-fullscreen-active');
        
        // Aplicar estilos diretamente
        container.style.position = 'fixed';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100vw';
        container.style.height = '100vh';
        container.style.zIndex = '9999';
        container.style.background = '#fff';
        
        // Ajustar área de edição
        setTimeout(() => {
            const editArea = container.querySelector('.tox-edit-area');
            if (editArea) {
                editArea.style.height = 'calc(100vh - 100px)';
            }
            
            const iframe = container.querySelector('.tox-edit-area iframe');
            if (iframe) {
                iframe.style.height = '100%';
            }
        }, 50);
        
        // Ocultar outros elementos
        this.hidePageElements();
    }
    
    exitCustomFullscreen(editor) {
        console.log('Exiting custom fullscreen');
        
        const container = editor.getContainer();
        const body = document.body;
        
        // Remover classes
        container.classList.remove('tox-fullscreen-custom');
        body.classList.remove('tox-fullscreen-active');
        
        // Remover estilos
        container.style.position = '';
        container.style.top = '';
        container.style.left = '';
        container.style.width = '';
        container.style.height = '';
        container.style.zIndex = '';
        container.style.background = '';
        
        // Restaurar área de edição
        const editArea = container.querySelector('.tox-edit-area');
        if (editArea) {
            editArea.style.height = '';
        }
        
        const iframe = container.querySelector('.tox-edit-area iframe');
        if (iframe) {
            iframe.style.height = '';
        }
        
        // Mostrar outros elementos
        this.showPageElements();
    }
    
    hidePageElements() {
        const elements = document.querySelectorAll('.navbar, .sidebar, footer, .breadcrumb');
        elements.forEach(el => {
            el.style.display = 'none';
        });
    }
    
    showPageElements() {
        const elements = document.querySelectorAll('.navbar, .sidebar, footer, .breadcrumb');
        elements.forEach(el => {
            el.style.display = '';
        });
    }
    
    setupEscapeListener() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const fullscreenEditor = document.querySelector('.tox-fullscreen-custom');
                if (fullscreenEditor) {
                    // Encontrar o editor correspondente
                    this.editors.forEach(editor => {
                        if (editor.getContainer() === fullscreenEditor) {
                            this.exitCustomFullscreen(editor);
                        }
                    });
                }
            }
        });
        
        console.log('Escape listener setup complete');
    }

    handleContentChange(editor) {
        // Auto-save se configurado
        this.triggerAutoSave(editor);
    }

    triggerAutoSave(editor) {
        if (this.autoSaveEnabled) {
            clearTimeout(this.autoSaveTimer);
            this.autoSaveTimer = setTimeout(() => {
                this.autoSave(editor);
            }, 30000); // 30 segundos
        }
    }

    autoSave(editor) {
        const content = editor.getContent();
        const title = document.getElementById('id_title')?.value || '';
        
        if (content && title) {
            const autoSaveData = {
                content: content,
                title: title,
                timestamp: new Date().toISOString()
            };
            
            try {
                localStorage.setItem(`tinymce_autosave_${editor.id}`, JSON.stringify(autoSaveData));
                this.showAutoSaveIndicator();
            } catch (e) {
                console.warn('Auto-save failed:', e);
            }
        }
    }

    showAutoSaveIndicator() {
        const indicator = document.getElementById('autosave-indicator');
        if (indicator) {
            indicator.style.display = 'inline-block';
            indicator.textContent = 'Salvo automaticamente';
            
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 3000);
        }
    }

    restoreAutoSave(editorId) {
        try {
            const savedData = localStorage.getItem(`tinymce_autosave_${editorId}`);
            if (savedData) {
                const data = JSON.parse(savedData);
                const savedTime = new Date(data.timestamp);
                const now = new Date();
                const hoursDiff = (now - savedTime) / (1000 * 60 * 60);
                
                // Só restaurar se foi salvo nas últimas 24 horas
                if (hoursDiff < 24) {
                    return data;
                }
            }
        } catch (e) {
            console.warn('Failed to restore auto-save:', e);
        }
        return null;
    }

    // Métodos públicos
    getEditor(id) {
        return this.editors.get(id);
    }

    getAllEditors() {
        return Array.from(this.editors.values());
    }

    clearAutoSave(editorId) {
        try {
            localStorage.removeItem(`tinymce_autosave_${editorId}`);
        } catch (e) {
            console.warn('Failed to clear auto-save:', e);
        }
    }
}

// CSS mínimo necessário
const tinyMCEStyle = document.createElement('style');
tinyMCEStyle.textContent = `
    /* Estilos básicos do editor */
    .tox-tinymce {
        border-radius: 0.375rem;
    }
    
    .tox-toolbar__primary {
        background: #f8f9fa !important;
    }
    
    .tox-editor-header {
        border-bottom: 1px solid #dee2e6;
    }
    
    .tox-statusbar {
        border-top: 1px solid #dee2e6;
        background: #f8f9fa !important;
    }
    
    /* CSS para fullscreen customizado */
    .tox-fullscreen-custom {
        transition: none !important;
    }
    
    .tox-fullscreen-active {
        overflow: hidden !important;
    }
    
    .tox-fullscreen-active .navbar,
    .tox-fullscreen-active .sidebar,
    .tox-fullscreen-active footer,
    .tox-fullscreen-active .breadcrumb {
        display: none !important;
    }
`;
document.head.appendChild(tinyMCEStyle);

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('TinyMCE Config: DOM loaded, initializing TinyMCEManager...');
    
    setTimeout(() => {
        try {
            window.tinyMCEManager = new TinyMCEManager();
            console.log('TinyMCE Config: TinyMCEManager created successfully');
        } catch (error) {
            console.error('TinyMCE Config: Error creating TinyMCEManager:', error);
        }
    }, 100);
});
