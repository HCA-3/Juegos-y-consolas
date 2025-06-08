// ===== CLIENTE API =====
class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    async request(method, endpoint, data = null, headers = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: method.toUpperCase(),
            headers: { ...this.defaultHeaders, ...headers }
        };

        if (data && ['POST', 'PUT', 'PATCH'].includes(config.method)) {
            if (data instanceof FormData) {
                // Para FormData, no establecer Content-Type (se establece automáticamente)
                delete config.headers['Content-Type'];
                config.body = data;
            } else {
                config.body = JSON.stringify(data);
            }
        }

        try {
            const response = await fetch(url, config);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            return result;
        } catch (error) {
            console.error(`API Error [${method} ${endpoint}]:`, error);
            throw error;
        }
    }

    // Métodos de conveniencia
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request('GET', url);
    }

    async post(endpoint, data) {
        return this.request('POST', endpoint, data);
    }

    async put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    }

    async delete(endpoint) {
        return this.request('DELETE', endpoint);
    }
}

// ===== SERVICIOS ESPECÍFICOS =====
class JuegosService {
    constructor(apiClient) {
        this.api = apiClient;
        this.endpoint = '/juegos';
    }

    async obtenerTodos(params = {}) {
        return this.api.get(this.endpoint, params);
    }

    async obtenerPorId(id) {
        return this.api.get(`${this.endpoint}/${id}`);
    }

    async crear(datos) {
        return this.api.post(this.endpoint, datos);
    }

    async actualizar(id, datos) {
        return this.api.put(`${this.endpoint}/${id}`, datos);
    }

    async eliminar(id) {
        return this.api.delete(`${this.endpoint}/${id}`);
    }

    async buscar(termino, params = {}) {
        return this.api.get(`${this.endpoint}/buscar`, { q: termino, ...params });
    }

    async obtenerPopulares(limit = 10) {
        return this.api.get(`${this.endpoint}/populares`, { limit });
    }

    async obtenerRecientes(limit = 10) {
        return this.api.get(`${this.endpoint}/recientes`, { limit });
    }

    async obtenerEstadisticas() {
        return this.api.get(`${this.endpoint}/estadisticas`);
    }

    async obtenerSugerencias(termino) {
        return this.api.get(`${this.endpoint}/sugerencias`, { q: termino });
    }
}

class ConsolasService {
    constructor(apiClient) {
        this.api = apiClient;
        this.endpoint = '/consolas';
    }

    async obtenerTodos(params = {}) {
        return this.api.get(this.endpoint, params);
    }

    async obtenerPorId(id) {
        return this.api.get(`${this.endpoint}/${id}`);
    }

    async crear(datos) {
        return this.api.post(this.endpoint, datos);
    }

    async actualizar(id, datos) {
        return this.api.put(`${this.endpoint}/${id}`, datos);
    }

    async eliminar(id) {
        return this.api.delete(`${this.endpoint}/${id}`);
    }

    async buscar(termino, params = {}) {
        return this.api.get(`${this.endpoint}/buscar`, { q: termino, ...params });
    }

    async obtenerPorFabricante(fabricante, params = {}) {
        return this.api.get(`${this.endpoint}/fabricantes/${fabricante}`, params);
    }

    async obtenerPorTipo(tipo, params = {}) {
        return this.api.get(`${this.endpoint}/tipos/${tipo}`, params);
    }

    async obtenerPorGeneracion(generacion, params = {}) {
        return this.api.get(`${this.endpoint}/generaciones/${generacion}`, params);
    }

    async obtenerRecientes(limit = 10) {
        return this.api.get(`${this.endpoint}/recientes`, { limit });
    }

    async obtenerEstadisticas() {
        return this.api.get(`${this.endpoint}/estadisticas`);
    }
}

class AccesoriosService {
    constructor(apiClient) {
        this.api = apiClient;
        this.endpoint = '/accesorios';
    }

    async obtenerTodos(params = {}) {
        return this.api.get(this.endpoint, params);
    }

    async obtenerPorId(id) {
        return this.api.get(`${this.endpoint}/${id}`);
    }

    async crear(datos) {
        return this.api.post(this.endpoint, datos);
    }

    async actualizar(id, datos) {
        return this.api.put(`${this.endpoint}/${id}`, datos);
    }

    async eliminar(id) {
        return this.api.delete(`${this.endpoint}/${id}`);
    }

    async buscar(termino, params = {}) {
        return this.api.get(`${this.endpoint}/buscar`, { q: termino, ...params });
    }

    async obtenerPorTipo(tipo, params = {}) {
        return this.api.get(`${this.endpoint}/tipos/${tipo}`, params);
    }

    async obtenerPorFabricante(fabricante, params = {}) {
        return this.api.get(`${this.endpoint}/fabricantes/${fabricante}`, params);
    }

    async obtenerPorCompatibilidad(compatibilidad, params = {}) {
        return this.api.get(`${this.endpoint}/compatibilidad/${compatibilidad}`, params);
    }

    async obtenerRecientes(limit = 10) {
        return this.api.get(`${this.endpoint}/recientes`, { limit });
    }

    async obtenerEstadisticas() {
        return this.api.get(`${this.endpoint}/estadisticas`);
    }
}

class CatalogoService {
    constructor(apiClient) {
        this.api = apiClient;
        this.endpoint = '/catalogo';
    }

    async obtenerResumen() {
        return this.api.get(this.endpoint);
    }

    async buscarGlobal(termino, params = {}) {
        return this.api.get(`${this.endpoint}/buscar`, { q: termino, ...params });
    }

    async obtenerDestacados() {
        return this.api.get(`${this.endpoint}/destacados`);
    }

    async obtenerEstadisticas() {
        return this.api.get(`${this.endpoint}/estadisticas`);
    }

    async obtenerPorCategoria(categoria, params = {}) {
        return this.api.get(`${this.endpoint}/categoria/${categoria}`, params);
    }

    async obtenerFiltros() {
        return this.api.get(`${this.endpoint}/filtros`);
    }
}

class ComparacionService {
    constructor(apiClient) {
        this.api = apiClient;
        this.endpoint = '/comparacion';
    }

    async obtenerInfo() {
        return this.api.get(this.endpoint);
    }

    async compararJuegos(ids) {
        return this.api.post(`${this.endpoint}/juegos`, { ids });
    }

    async compararConsolas(ids) {
        return this.api.post(`${this.endpoint}/consolas`, { ids });
    }

    async compararAccesorios(ids) {
        return this.api.post(`${this.endpoint}/accesorios`, { ids });
    }

    async compararJuegosGet(ids) {
        return this.api.get(`${this.endpoint}/juegos`, { ids: ids.join(',') });
    }

    async compararConsolasGet(ids) {
        return this.api.get(`${this.endpoint}/consolas`, { ids: ids.join(',') });
    }

    async compararAccesoriosGet(ids) {
        return this.api.get(`${this.endpoint}/accesorios`, { ids: ids.join(',') });
    }
}

// ===== INSTANCIA GLOBAL =====
const API = new APIClient();

// Servicios específicos
const JuegosAPI = new JuegosService(API);
const ConsolasAPI = new ConsolasService(API);
const AccesoriosAPI = new AccesoriosService(API);
const CatalogoAPI = new CatalogoService(API);
const ComparacionAPI = new ComparacionService(API);

// ===== UTILIDADES DE DATOS =====
class DataUtils {
    static async cargarDatos(servicio, metodo, ...args) {
        try {
            Utils.showLoading();
            const response = await servicio[metodo](...args);
            
            if (response.success) {
                return response.data;
            } else {
                throw new Error(response.error || 'Error al cargar datos');
            }
        } catch (error) {
            console.error('Error cargando datos:', error);
            Utils.showToast(error.message || 'Error al cargar datos', 'error');
            return null;
        } finally {
            Utils.hideLoading();
        }
    }

    static async guardarDatos(servicio, metodo, datos, mensajeExito = 'Datos guardados exitosamente') {
        try {
            Utils.showLoading();
            const response = await servicio[metodo](datos);
            
            if (response.success) {
                Utils.showToast(response.message || mensajeExito, 'success');
                return response.data;
            } else {
                throw new Error(response.error || 'Error al guardar datos');
            }
        } catch (error) {
            console.error('Error guardando datos:', error);
            Utils.showToast(error.message || 'Error al guardar datos', 'error');
            return null;
        } finally {
            Utils.hideLoading();
        }
    }

    static async eliminarDatos(servicio, id, mensajeExito = 'Elemento eliminado exitosamente') {
        try {
            const confirmacion = await this.confirmarEliminacion();
            if (!confirmacion) return false;

            Utils.showLoading();
            const response = await servicio.eliminar(id);
            
            if (response.success) {
                Utils.showToast(response.message || mensajeExito, 'success');
                return true;
            } else {
                throw new Error(response.error || 'Error al eliminar');
            }
        } catch (error) {
            console.error('Error eliminando datos:', error);
            Utils.showToast(error.message || 'Error al eliminar', 'error');
            return false;
        } finally {
            Utils.hideLoading();
        }
    }

    static confirmarEliminacion() {
        return new Promise((resolve) => {
            const modal = Modal.create(
                'Confirmar Eliminación',
                '<p>¿Estás seguro de que deseas eliminar este elemento? Esta acción no se puede deshacer.</p>',
                [
                    {
                        text: 'Cancelar',
                        class: 'btn-outline',
                        onclick: `document.getElementById('${modal.modal.id}').closest('.modal-overlay').classList.remove('active'); window.resolveDelete(false);`
                    },
                    {
                        text: 'Eliminar',
                        class: 'btn-danger',
                        onclick: `document.getElementById('${modal.modal.id}').closest('.modal-overlay').classList.remove('active'); window.resolveDelete(true);`
                    }
                ]
            );

            window.resolveDelete = (result) => {
                resolve(result);
                delete window.resolveDelete;
                modal.close();
            };

            modal.open();
        });
    }
}

// ===== RENDERIZADORES =====
class Renderers {
    static renderCard(item, tipo = 'juego') {
        const precio = Utils.formatPrice(item.precio);
        const fecha = Utils.formatDate(item.fecha_lanzamiento || item.fecha_creacion);
        
        let extraInfo = '';
        switch (tipo) {
            case 'juego':
                extraInfo = `
                    <div class="card-meta">
                        <span class="badge badge-primary">${item.genero || 'N/A'}</span>
                        <span class="badge badge-secondary">${item.plataforma || 'N/A'}</span>
                        ${item.calificacion ? `<span class="rating">${Utils.formatRating(item.calificacion)}</span>` : ''}
                    </div>
                `;
                break;
            case 'consola':
                extraInfo = `
                    <div class="card-meta">
                        <span class="badge badge-primary">${item.fabricante || 'N/A'}</span>
                        <span class="badge badge-secondary">${item.tipo || 'N/A'}</span>
                        ${item.generacion ? `<span class="badge badge-accent">Gen ${item.generacion}</span>` : ''}
                    </div>
                `;
                break;
            case 'accesorio':
                extraInfo = `
                    <div class="card-meta">
                        <span class="badge badge-primary">${item.tipo || 'N/A'}</span>
                        <span class="badge badge-secondary">${item.fabricante || 'N/A'}</span>
                        ${item.compatibilidad ? `<span class="badge badge-accent">${item.compatibilidad}</span>` : ''}
                    </div>
                `;
                break;
        }

        return `
            <div class="card" data-id="${item.id}" data-tipo="${tipo}">
                ${item.imagen_url ? `<img src="${item.imagen_url}" alt="${item.nombre}" class="card-image">` : ''}
                <div class="card-header">
                    <div>
                        <h3 class="card-title">${item.nombre}</h3>
                        <p class="card-subtitle">${item.desarrollador || item.fabricante || 'N/A'}</p>
                    </div>
                    <div class="card-actions">
                        <button class="btn btn-sm btn-outline" onclick="verDetalle('${tipo}', ${item.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="editarItem('${tipo}', ${item.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="eliminarItem('${tipo}', ${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <p class="card-description">${Utils.truncateText(item.descripcion || 'Sin descripción', 120)}</p>
                    ${extraInfo}
                </div>
                <div class="card-footer">
                    <div class="card-price">
                        <strong>${precio}</strong>
                    </div>
                    <div class="card-date">
                        <small class="text-muted">${fecha}</small>
                    </div>
                </div>
            </div>
        `;
    }

    static renderTable(items, tipo = 'juego', columns = []) {
        if (!items || items.length === 0) {
            return '<div class="alert alert-info">No se encontraron elementos</div>';
        }

        const defaultColumns = {
            juego: ['nombre', 'genero', 'plataforma', 'precio', 'calificacion', 'acciones'],
            consola: ['nombre', 'fabricante', 'tipo', 'generacion', 'precio', 'acciones'],
            accesorio: ['nombre', 'tipo', 'fabricante', 'compatibilidad', 'precio', 'acciones']
        };

        const cols = columns.length > 0 ? columns : defaultColumns[tipo] || defaultColumns.juego;

        const headers = cols.map(col => {
            const titles = {
                nombre: 'Nombre',
                genero: 'Género',
                plataforma: 'Plataforma',
                precio: 'Precio',
                calificacion: 'Calificación',
                fabricante: 'Fabricante',
                tipo: 'Tipo',
                generacion: 'Generación',
                compatibilidad: 'Compatibilidad',
                acciones: 'Acciones'
            };
            return `<th>${titles[col] || col}</th>`;
        }).join('');

        const rows = items.map(item => {
            const cells = cols.map(col => {
                switch (col) {
                    case 'precio':
                        return `<td>${Utils.formatPrice(item.precio)}</td>`;
                    case 'calificacion':
                        return `<td>${item.calificacion ? Utils.formatRating(item.calificacion) : 'N/A'}</td>`;
                    case 'acciones':
                        return `
                            <td>
                                <div class="btn-group">
                                    <button class="btn btn-sm btn-outline" onclick="verDetalle('${tipo}', ${item.id})" title="Ver">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-sm btn-primary" onclick="editarItem('${tipo}', ${item.id})" title="Editar">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-danger" onclick="eliminarItem('${tipo}', ${item.id})" title="Eliminar">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        `;
                    default:
                        return `<td>${item[col] || 'N/A'}</td>`;
                }
            }).join('');
            return `<tr data-id="${item.id}">${cells}</tr>`;
        }).join('');

        return `
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>${headers}</tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        `;
    }

    static renderPagination(paginationData, onPageChange) {
        if (!paginationData || paginationData.pages <= 1) return '';

        const { current_page, pages, has_prev, has_next } = paginationData;
        let html = '<div class="pagination">';

        // Botón anterior
        if (has_prev) {
            html += `<a href="#" class="pagination-item" onclick="${onPageChange}(${current_page - 1})">
                <i class="fas fa-chevron-left"></i>
            </a>`;
        }

        // Números de página
        const startPage = Math.max(1, current_page - 2);
        const endPage = Math.min(pages, current_page + 2);

        if (startPage > 1) {
            html += `<a href="#" class="pagination-item" onclick="${onPageChange}(1)">1</a>`;
            if (startPage > 2) {
                html += '<span class="pagination-item">...</span>';
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            html += `<a href="#" class="pagination-item ${i === current_page ? 'active' : ''}" 
                     onclick="${onPageChange}(${i})">${i}</a>`;
        }

        if (endPage < pages) {
            if (endPage < pages - 1) {
                html += '<span class="pagination-item">...</span>';
            }
            html += `<a href="#" class="pagination-item" onclick="${onPageChange}(${pages})">${pages}</a>`;
        }

        // Botón siguiente
        if (has_next) {
            html += `<a href="#" class="pagination-item" onclick="${onPageChange}(${current_page + 1})">
                <i class="fas fa-chevron-right"></i>
            </a>`;
        }

        html += '</div>';
        return html;
    }
}

// ===== EXPORTAR PARA USO GLOBAL =====
window.API = API;
window.JuegosAPI = JuegosAPI;
window.ConsolasAPI = ConsolasAPI;
window.AccesoriosAPI = AccesoriosAPI;
window.CatalogoAPI = CatalogoAPI;
window.ComparacionAPI = ComparacionAPI;
window.DataUtils = DataUtils;
window.Renderers = Renderers;

