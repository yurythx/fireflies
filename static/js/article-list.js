/**
 * Funcionalidades interativas para a listagem de artigos
 */

document.addEventListener('DOMContentLoaded', function() {
    // Animação de entrada dos artigos
    const articles = document.querySelectorAll('.article-item');
    
    // Intersection Observer para animações de entrada
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const articleObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                articleObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Aplicar animação inicial
    articles.forEach((article, index) => {
        article.style.opacity = '0';
        article.style.transform = 'translateY(20px)';
        article.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        articleObserver.observe(article);
    });
    
    // Efeito hover nas imagens
    const featuredImages = document.querySelectorAll('.featured-image');
    featuredImages.forEach(image => {
        image.addEventListener('mouseenter', function() {
            this.querySelector('img').style.transform = 'scale(1.02)';
            this.querySelector('.image-overlay').style.opacity = '1';
        });
        
        image.addEventListener('mouseleave', function() {
            this.querySelector('img').style.transform = 'scale(1)';
            this.querySelector('.image-overlay').style.opacity = '0';
        });
    });
    
    // Contador de visualizações em tempo real (simulado)
    const viewCounters = document.querySelectorAll('.views');
    viewCounters.forEach(counter => {
        const currentCount = parseInt(counter.textContent.match(/\d+/)[0]);
        const newCount = currentCount + Math.floor(Math.random() * 3) + 1;
        
        // Animação do contador
        animateCounter(counter, currentCount, newCount);
    });
    
    // Filtros de categoria e tag
    const categoryLinks = document.querySelectorAll('.category-links a, .article-tags a');
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const filter = this.getAttribute('href').split('=')[1];
            const filterType = this.closest('.category-links') ? 'category' : 'tag';
            
            // Adicionar indicador visual de filtro ativo
            document.querySelectorAll('.filter-active').forEach(el => {
                el.classList.remove('filter-active');
            });
            this.classList.add('filter-active');
            
            // Simular filtro (em uma implementação real, isso faria uma requisição AJAX)
            console.log(`Filtrando por ${filterType}: ${filter}`);
        });
    });
    
    // Busca em tempo real no sidebar
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = this.value.trim();
                if (query.length >= 2) {
                    // Simular busca em tempo real
                    console.log(`Buscando por: ${query}`);
                }
            }, 300);
        });
    }
    
    // Lazy loading para imagens
    const images = document.querySelectorAll('.featured-image img, .featured-image-simple img');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src || img.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => {
        if (img.dataset.src) {
            imageObserver.observe(img);
        }
    });
    
    // Força tamanhos fixos para imagens após carregamento
    function enforceImageSizes() {
        const featuredImages = document.querySelectorAll('.featured-image, .featured-image-simple');
        featuredImages.forEach(container => {
            const img = container.querySelector('img');
            if (img) {
                // Força o tamanho correto
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'cover';
                img.style.objectPosition = 'center';
                img.style.flexShrink = '0';
                
                // Força o container também
                container.style.width = '100%';
                container.style.flexShrink = '0';
                
                // Remove classes que possam interferir
                img.classList.remove('img-fluid', 'img-thumbnail');
            }
        });
    }
    
    // Executa após carregamento das imagens
    window.addEventListener('load', enforceImageSizes);
    
    // Executa quando as imagens carregam
    images.forEach(img => {
        img.addEventListener('load', enforceImageSizes);
        img.addEventListener('error', enforceImageSizes);
    });
    
    // Executa periodicamente para garantir consistência
    setInterval(enforceImageSizes, 1000);
    
    // Tooltips para informações adicionais
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = this.dataset.tooltip;
            tooltip.style.cssText = `
                position: absolute;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 1000;
                pointer-events: none;
                white-space: nowrap;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
            
            this.tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this.tooltip) {
                this.tooltip.remove();
                this.tooltip = null;
            }
        });
    });
    
    // Função para animar contadores
    function animateCounter(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(start + (end - start) * progress);
            const text = element.textContent.replace(/\d+/, current);
            element.textContent = text;
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        }
        
        requestAnimationFrame(updateCounter);
    }
    
    // Melhorias de acessibilidade
    const articleLinks = document.querySelectorAll('.article-title a, .featured-image a');
    articleLinks.forEach(link => {
        link.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Indicador de carregamento para ações
    const actionButtons = document.querySelectorAll('.btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.classList.contains('loading')) {
                this.classList.add('loading');
                this.dataset.originalText = this.textContent;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Carregando...';
                
                // Simular tempo de carregamento
                setTimeout(() => {
                    this.classList.remove('loading');
                    this.textContent = this.dataset.originalText;
                }, 1000);
            }
        });
    });
    
    // Estatísticas em tempo real (simulado)
    updateStats();
    
    function updateStats() {
        const statsElements = document.querySelectorAll('.stats-counter');
        statsElements.forEach(element => {
            const currentValue = parseInt(element.textContent);
            const newValue = currentValue + Math.floor(Math.random() * 5) + 1;
            
            setTimeout(() => {
                animateCounter(element, currentValue, newValue);
            }, Math.random() * 5000);
        });
        
        // Atualizar a cada 30 segundos
        setTimeout(updateStats, 30000);
    }
});

// Funções utilitárias
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
} 