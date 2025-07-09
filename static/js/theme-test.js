/**
 * Script de teste para verificar a funcionalidade dos temas
 */

class ThemeTester {
    constructor() {
        this.init();
    }

    init() {
        this.createTestUI();
        this.bindEvents();
        this.runTests();
    }

    createTestUI() {
        // Criar painel de teste se não existir
        if (document.getElementById('theme-test-panel')) return;

        const panel = document.createElement('div');
        panel.id = 'theme-test-panel';
        panel.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-color);
            border: 2px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            z-index: 9999;
            min-width: 250px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            font-family: monospace;
            font-size: 12px;
        `;

        panel.innerHTML = `
            <h4 style="margin: 0 0 10px 0; color: var(--text-color);">🧪 Teste de Temas</h4>
            <div style="margin-bottom: 10px;">
                <button id="test-light" style="margin-right: 5px; padding: 5px 10px;">Claro</button>
                <button id="test-dark" style="margin-right: 5px; padding: 5px 10px;">Escuro</button>
                <button id="test-toggle" style="padding: 5px 10px;">Alternar</button>
            </div>
            <div id="test-results" style="color: var(--text-color);">
                <div>Status: <span id="current-theme">Carregando...</span></div>
                <div>CSS Variables: <span id="css-vars">Verificando...</span></div>
                <div>Drawer: <span id="drawer-status">Verificando...</span></div>
                <div>Contraste: <span id="contrast-status">Verificando...</span></div>
            </div>
            <button id="close-test" style="position: absolute; top: 5px; right: 5px; background: none; border: none; color: var(--text-color); cursor: pointer; font-size: 16px;">×</button>
        `;

        document.body.appendChild(panel);
    }

    bindEvents() {
        document.getElementById('test-light')?.addEventListener('click', () => {
            this.setTheme('light');
        });

        document.getElementById('test-dark')?.addEventListener('click', () => {
            this.setTheme('dark');
        });

        document.getElementById('test-toggle')?.addEventListener('click', () => {
            const current = this.getCurrentTheme();
            this.setTheme(current === 'light' ? 'dark' : 'light');
        });

        document.getElementById('close-test')?.addEventListener('click', () => {
            document.getElementById('theme-test-panel')?.remove();
        });
    }

    setTheme(theme) {
        if (window.djangoTheme) {
            window.djangoTheme.setTheme(theme);
        } else {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('django-theme', theme);
        }
        this.updateResults();
    }

    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }

    checkCSSVariables() {
        const root = document.documentElement;
        const computedStyle = getComputedStyle(root);
        
        const requiredVars = [
            '--bg-color',
            '--text-color',
            '--border-color',
            '--primary-color'
        ];

        const missing = requiredVars.filter(varName => {
            const value = computedStyle.getPropertyValue(varName);
            return !value || value.trim() === '';
        });

        return missing.length === 0 ? '✅ OK' : `❌ Faltando: ${missing.join(', ')}`;
    }

    checkDrawer() {
        const drawer = document.querySelector('.navbar-collapse');
        if (!drawer) return '❌ Drawer não encontrado';
        
        const styles = getComputedStyle(drawer);
        const bgColor = styles.backgroundColor;
        
        if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)') {
            return '✅ Visível';
        } else {
            return '❌ Invisível';
        }
    }
    
    checkContrast() {
        const elements = [
            '.navbar-nav .nav-link',
            '.navbar-collapse .form-django input',
            '.navbar-collapse .theme-toggle .theme-option',
            '.navbar-collapse .btn-outline-light'
        ];
        
        const issues = [];
        
        elements.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                const styles = getComputedStyle(element);
                const color = styles.color;
                const bgColor = styles.backgroundColor;
                
                // Verificar se as cores estão definidas
                if (!color || color === 'rgba(0, 0, 0, 0)' || color === 'transparent') {
                    issues.push(`${selector} - cor indefinida`);
                }
                if (!bgColor || bgColor === 'rgba(0, 0, 0, 0)' || bgColor === 'transparent') {
                    issues.push(`${selector} - background indefinido`);
                }
            }
        });
        
        return issues.length === 0 ? '✅ OK' : `❌ ${issues.length} problemas`;
    }

    updateResults() {
        const currentTheme = this.getCurrentTheme();
        const cssVars = this.checkCSSVariables();
        const drawerStatus = this.checkDrawer();
        const contrastStatus = this.checkContrast();

        document.getElementById('current-theme').textContent = currentTheme;
        document.getElementById('css-vars').textContent = cssVars;
        document.getElementById('drawer-status').textContent = drawerStatus;
        document.getElementById('contrast-status').textContent = contrastStatus;

        // Atualizar cores do painel
        const panel = document.getElementById('theme-test-panel');
        if (panel) {
            panel.style.background = getComputedStyle(document.documentElement).getPropertyValue('--bg-color');
            panel.style.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color');
            panel.style.color = getComputedStyle(document.documentElement).getPropertyValue('--text-color');
        }
    }

    runTests() {
        setTimeout(() => {
            this.updateResults();
        }, 100);
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    // Só mostrar em desenvolvimento
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        new ThemeTester();
    }
});

// Atalho de teclado para mostrar/ocultar o painel
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        const panel = document.getElementById('theme-test-panel');
        if (panel) {
            panel.remove();
        } else {
            new ThemeTester();
        }
    }
}); 