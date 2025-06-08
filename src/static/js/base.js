// ===== CONFIGURACIÓN GLOBAL =====
const CONFIG = {
    API_BASE_URL: '/api',
    TOAST_DURATION: 5000,
    LOADING_MIN_TIME: 500
};

// ===== UTILIDADES GLOBALES =====
class Utils {
    static showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('active');
        }
    }

    static hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            setTimeout(() => {
                overlay.classList.remove('active');
            }, CONFIG.LOADING_MIN_TIME);
        }
    }

    static showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="toast-icon fas ${this.getToastIcon(type)}"></i>
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Estilos del toast
        toast.style.cssText = `
            background: var(--bg-card);
            border: 2px solid var(--${type === 'error' ? 'danger' : type === 'success' ? 'primary' : 'accent'}-color);
            border-radius: var(--border-radius);
            padding: var(--spacing-md);
            margin-bottom: var(--spacing-sm);
            box-shadow: var(--shadow-lg);
            transform: translateX(100%);
            transition: var(--transition-fast);
            max-width: 400px;
        `;

        container.appendChild(toast);

        // Animación de entrada
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 10);

        // Auto-remove
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }, CONFIG.TOAST_DURATION);
    }

    static getToastIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    static formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    static formatPrice(price) {
        if (price === null || price === undefined) return 'N/A';
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'USD'
        }).format(price);
    }

    static formatRating(rating) {
        if (!rating) return 'N/A';
        const stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
        return `${stars} (${rating}/5)`;
    }

    static debounce(func, wait) {
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

    static truncateText(text, maxLength = 100) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    static generateId() {
        return Math.random().toString(36).substr(2, 9);
    }
}

// ===== NAVEGACIÓN =====
class Navigation {
    constructor() {
        this.init();
    }

    init() {
        this.setupMobileMenu();
        this.setupDropdowns();
        this.setupGlobalSearch();
        this.setupActiveLinks();
    }

    setupMobileMenu() {
        const toggle = document.querySelector('.mobile-menu-toggle');
        const menu = document.querySelector('.nav-menu');

        if (toggle && menu) {
            toggle.addEventListener('click', () => {
                menu.classList.toggle('active');
                toggle.classList.toggle('active');
            });

            // Cerrar menu al hacer click fuera
            document.addEventListener('click', (e) => {
                if (!toggle.contains(e.target) && !menu.contains(e.target)) {
                    menu.classList.remove('active');
                    toggle.classList.remove('active');
                }
            });
        }
    }

    setupDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown');
        
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');

            if (toggle && menu) {
                // Hover para desktop
                dropdown.addEventListener('mouseenter', () => {
                    menu.style.display = 'block';
                });

                dropdown.addEventListener('mouseleave', () => {
                    menu.style.display = 'none';
                });

                // Click para mobile
                toggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    const isVisible = menu.style.display === 'block';
                    
                    // Cerrar otros dropdowns
                    dropdowns.forEach(other => {
                        if (other !== dropdown) {
                            other.querySelector('.dropdown-menu').style.display = 'none';
                        }
                    });

                    menu.style.display = isVisible ? 'none' : 'block';
                });
            }
        });

        // Cerrar dropdowns al hacer click fuera
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                dropdowns.forEach(dropdown => {
                    dropdown.querySelector('.dropdown-menu').style.display = 'none';
                });
            }
        });
    }

    setupGlobalSearch() {
        const form = document.getElementById('globalSearchForm');
        const input = document.getElementById('globalSearchInput');

        if (form && input) {
            const debouncedSearch = Utils.debounce(this.performGlobalSearch.bind(this), 300);

            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performGlobalSearch(input.value.trim());
            });

            input.addEventListener('input', (e) => {
                const query = e.target.value.trim();
                if (query.length >= 2) {
                    debouncedSearch(query);
                }
            });
        }
    }

    async performGlobalSearch(query) {
        if (!query) return;

        try {
            Utils.showLoading();
            const response = await API.get(`/catalogo/buscar?q=${encodeURIComponent(query)}`);
            
            if (response.success) {
                // Redirigir a página de resultados o mostrar resultados
                window.location.href = `/buscar?q=${encodeURIComponent(query)}`;
            }
        } catch (error) {
            console.error('Error en búsqueda global:', error);
            Utils.showToast('Error al realizar la búsqueda', 'error');
        } finally {
            Utils.hideLoading();
        }
    }

    setupActiveLinks() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.startsWith(href) && href !== '/') {
                link.classList.add('active');
            }
        });
    }
}

// ===== MODALES =====
class Modal {
    constructor(modalId) {
        this.modal = document.getElementById(modalId);
        this.overlay = this.modal?.closest('.modal-overlay');
        this.init();
    }

    init() {
        if (!this.modal || !this.overlay) return;

        // Botón de cerrar
        const closeBtn = this.modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // Cerrar al hacer click en overlay
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });

        // Cerrar con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });
    }

    open() {
        if (this.overlay) {
            this.overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    close() {
        if (this.overlay) {
            this.overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    isOpen() {
        return this.overlay?.classList.contains('active');
    }

    static create(title, content, actions = []) {
        const modalId = `modal-${Utils.generateId()}`;
        const modalHTML = `
            <div class="modal-overlay" id="${modalId}-overlay">
                <div class="modal" id="${modalId}">
                    <div class="modal-header">
                        <h3 class="modal-title">${title}</h3>
                        <button class="modal-close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                    ${actions.length > 0 ? `
                        <div class="modal-footer">
                            ${actions.map(action => `
                                <button class="btn ${action.class || 'btn-primary'}" 
                                        onclick="${action.onclick || ''}"
                                        ${action.attributes || ''}>
                                    ${action.text}
                                </button>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        return new Modal(modalId);
    }
}

// ===== FORMULARIOS =====
class FormHandler {
    constructor(formElement) {
        this.form = formElement;
        this.init();
    }

    init() {
        if (!this.form) return;

        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });

        // Validación en tiempo real
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }

    async handleSubmit() {
        if (!this.validateForm()) return;

        const formData = new FormData(this.form);
        const data = Object.fromEntries(formData.entries());

        try {
            Utils.showLoading();
            
            const method = this.form.dataset.method || 'POST';
            const url = this.form.action || this.form.dataset.url;
            
            const response = await API.request(method, url, data);
            
            if (response.success) {
                Utils.showToast(response.message || 'Operación exitosa', 'success');
                
                // Callback personalizado
                if (this.form.dataset.onSuccess) {
                    window[this.form.dataset.onSuccess](response);
                }
                
                // Redirección
                if (this.form.dataset.redirect) {
                    setTimeout(() => {
                        window.location.href = this.form.dataset.redirect;
                    }, 1000);
                }
            } else {
                throw new Error(response.error || 'Error en el formulario');
            }
        } catch (error) {
            console.error('Error en formulario:', error);
            Utils.showToast(error.message || 'Error al procesar el formulario', 'error');
        } finally {
            Utils.hideLoading();
        }
    }

    validateForm() {
        const inputs = this.form.querySelectorAll('input, select, textarea');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        const rules = this.getValidationRules(field);
        let isValid = true;
        let errorMessage = '';

        // Required
        if (rules.required && !value) {
            errorMessage = 'Este campo es requerido';
            isValid = false;
        }

        // Email
        if (rules.email && value && !this.isValidEmail(value)) {
            errorMessage = 'Ingrese un email válido';
            isValid = false;
        }

        // Min length
        if (rules.minLength && value.length < rules.minLength) {
            errorMessage = `Mínimo ${rules.minLength} caracteres`;
            isValid = false;
        }

        // Max length
        if (rules.maxLength && value.length > rules.maxLength) {
            errorMessage = `Máximo ${rules.maxLength} caracteres`;
            isValid = false;
        }

        // Number
        if (rules.number && value && isNaN(value)) {
            errorMessage = 'Debe ser un número válido';
            isValid = false;
        }

        // Min value
        if (rules.min && parseFloat(value) < rules.min) {
            errorMessage = `Valor mínimo: ${rules.min}`;
            isValid = false;
        }

        // Max value
        if (rules.max && parseFloat(value) > rules.max) {
            errorMessage = `Valor máximo: ${rules.max}`;
            isValid = false;
        }

        this.showFieldError(field, errorMessage);
        return isValid;
    }

    getValidationRules(field) {
        return {
            required: field.hasAttribute('required'),
            email: field.type === 'email',
            number: field.type === 'number',
            minLength: field.getAttribute('minlength'),
            maxLength: field.getAttribute('maxlength'),
            min: field.getAttribute('min'),
            max: field.getAttribute('max')
        };
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    showFieldError(field, message) {
        this.clearFieldError(field);

        if (message) {
            field.classList.add('error');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error';
            errorDiv.textContent = message;
            field.parentNode.appendChild(errorDiv);
        }
    }

    clearFieldError(field) {
        field.classList.remove('error');
        const errorDiv = field.parentNode.querySelector('.form-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
}

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar navegación
    new Navigation();

    // Inicializar formularios
    const forms = document.querySelectorAll('form[data-ajax]');
    forms.forEach(form => new FormHandler(form));

    // Inicializar modales existentes
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => new Modal(modal.id));

    // Efectos de scroll
    window.addEventListener('scroll', () => {
        const header = document.querySelector('.main-header');
        if (header) {
            if (window.scrollY > 100) {
                header.style.background = 'var(--bg-overlay)';
                header.style.backdropFilter = 'blur(15px)';
            } else {
                header.style.background = 'var(--bg-overlay)';
                header.style.backdropFilter = 'blur(10px)';
            }
        }
    });

    // Animaciones de entrada
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observar elementos animables
    const animatedElements = document.querySelectorAll('.card, .table-container, .alert');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// ===== EXPORTAR PARA USO GLOBAL =====
window.Utils = Utils;
window.Modal = Modal;
window.FormHandler = FormHandler;

