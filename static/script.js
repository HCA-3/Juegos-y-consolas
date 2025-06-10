// Función para búsqueda rápida
async function buscarRapida() {
    const query = document.getElementById('search-query').value.trim();
    const tipo = document.getElementById('search-type').value;
    
    if (!query) {
        alert('Por favor ingresa un término de búsqueda');
        return;
    }
    
    try {
        const response = await fetch(`/api/buscar?q=${encodeURIComponent(query)}&tipo=${tipo}`);
        const resultados = await response.json();
        
        mostrarResultados(resultados);
    } catch (error) {
        alert('Error al buscar: ' + error.message);
        console.error(error);
    }
}

// Mostrar resultados de búsqueda
function mostrarResults(resultados) { // Cambiado a mostrarResults para evitar conflicto si ya tienes una función mostrarResultados
    const container = document.getElementById('search-results');
    container.innerHTML = '';
    
    if (!resultados || Object.keys(resultados).length === 0) {
        container.innerHTML = '<p class="no-results">No se encontraron resultados</p>';
        return;
    }
    
    for (const [tipo, items] of Object.entries(resultados)) {
        if (!items || !Array.isArray(items) || items.length === 0) continue;
        
        const tipoNombre = tipo === 'juegos' ? 'Juegos' : 
                         tipo === 'consolas' ? 'Consolas' : 'Accesorios';
        
        const section = document.createElement('div');
        section.className = `search-result-section`;
        section.innerHTML = `<h3>${tipoNombre}</h3>`;
        
        items.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = `search-result-item result-type-${tipo}`;
            
            let html = `<h4>${item.nombre}</h4>`;
            
            if (item.genero) html += `<p><strong>Género:</strong> ${item.genero}</p>`;
            if (item.año || item.año_lanzamiento) html += `<p><strong>Año:</strong> ${item.año || item.año_lanzamiento}</p>`;
            if (item.desarrollador) html += `<p><strong>Desarrollador:</strong> ${item.desarrollador}</p>`;
            if (item.fabricante) html += `<p><strong>Fabricante:</strong> ${item.fabricante}</p>`;
            if (item.tipo) html += `<p><strong>Tipo:</strong> ${item.tipo}</p>`;
            if (item.compatible_con) html += `<p><strong>Compatibilidad:</strong> ${item.compatible_con}</p>`;
            
            // Mostrar imagen de Cloudinary
            if (item.imagen) {
                html += `<img src="${item.imagen}" alt="${item.nombre}" class="minecraft-img">`;
            }
            
            itemElement.innerHTML = html;
            section.appendChild(itemElement);
        });
        
        container.appendChild(section);
    }
}


// --- Funciones para crear, actualizar y eliminar (MODIFICADAS para usar FormData y preview de imagen) ---

// --- JUEGOS ---
async function cargarJuegos() {
    try {
        const response = await fetch('/api/juegos/');
        const juegos = await response.json();
        const container = document.getElementById('juegos-container');
        container.innerHTML = ''; // Limpiar antes de añadir
        if (juegos.length === 0) {
            container.innerHTML = '<p class="no-results">No hay juegos registrados.</p>';
            return;
        }
        juegos.forEach(juego => {
            const juegoDiv = document.createElement('div');
            juegoDiv.className = 'grid-item';
            juegoDiv.innerHTML = `
                <h3>${juego.nombre}</h3>
                <p><strong>Género:</strong> ${juego.genero}</p>
                <p><strong>Año:</strong> ${juego.año || 'N/A'}</p>
                <p><strong>Desarrollador:</strong> ${juego.desarrollador || 'N/A'}</p>
                ${juego.imagen ? `<img src="${juego.imagen}" alt="${juego.nombre}" class="item-img">` : '<div class="no-image">No Image</div>'}
                <div class="item-actions">
                    <button class="btn btn-secondary" onclick="abrirModalEditarJuego(${juego.id})">Editar</button>
                    <button class="btn btn-danger" onclick="eliminarJuego(${juego.id})">Eliminar</button>
                </div>
            `;
            container.appendChild(juegoDiv);
        });
    } catch (error) {
        console.error('Error al cargar juegos:', error);
        alert('Error al cargar juegos: ' + error.message);
    }
}

async function crearJuego(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form); 

    try {
        const response = await fetch('/api/juegos/', {
            method: 'POST',
            body: formData 
        });
        
        if (response.ok) {
            alert('Juego creado con éxito!');
            form.reset(); 
            // Resetear previsualización también
            document.getElementById('juego-imagen-preview').src = '';
            document.getElementById('juego-imagen-preview').style.display = 'none';
            cargarJuegos(); 
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error desconocido');
        }
    } catch (error) {
        alert('Error al crear juego: ' + error.message);
        console.error(error);
    }
}

let currentEditJuegoId = null; 

async function abrirModalEditarJuego(juegoId) {
    currentEditJuegoId = juegoId;
    const modal = document.getElementById('juego-edit-modal');
    const form = document.getElementById('juego-edit-form');
    
    // Resetear formulario y previsualización de imagen
    form.reset();
    document.getElementById('edit-juego-imagen-preview').src = '';
    document.getElementById('edit-juego-imagen-preview').style.display = 'none';
    document.getElementById('mantener-juego-imagen-checkbox').checked = false;


    try {
        const response = await fetch(`/api/juegos/?q=&skip=0&limit=1000`); 
        const juegos = await response.json();
        const juego = juegos.find(j => j.id === juegoId);

        if (juego) {
            document.getElementById('edit-juego-nombre').value = juego.nombre;
            document.getElementById('edit-juego-genero').value = juego.genero;
            document.getElementById('edit-juego-anio').value = juego.año || '';
            document.getElementById('edit-juego-desarrollador').value = juego.desarrollador || '';
            
            const imgPreview = document.getElementById('edit-juego-imagen-preview');
            const mantenerCheckbox = document.getElementById('mantener-juego-imagen-checkbox');

            if (juego.imagen) {
                imgPreview.src = juego.imagen;
                imgPreview.style.display = 'block';
                mantenerCheckbox.checked = true; 
            } else {
                imgPreview.style.display = 'none';
                imgPreview.src = '';
                mantenerCheckbox.checked = false; 
            }
            modal.style.display = 'block';
        } else {
            alert('Juego no encontrado.');
        }
    } catch (error) {
        alert('Error al cargar datos del juego para editar: ' + error.message);
        console.error(error);
    }
}

async function actualizarJuego(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(); 

    // Añadir los campos de texto
    formData.append('nombre', form.elements['edit-juego-nombre'].value);
    formData.append('genero', form.elements['edit-juego-genero'].value);
    formData.append('año', form.elements['edit-juego-anio'].value);
    formData.append('desarrollador', form.elements['edit-juego-desarrollador'].value);
    
    // Añadir el archivo de imagen si existe y no está vacío
    const imagenInput = form.elements['edit-juego-imagen'];
    if (imagenInput.files && imagenInput.files[0]) {
        formData.append('imagen', imagenInput.files[0]);
    } else {
        formData.append('mantener_imagen_existente', form.elements['mantener-juego-imagen-checkbox'].checked ? 'true' : 'false');
    }

    try {
        const response = await fetch(`/api/juegos/${currentEditJuegoId}`, {
            method: 'PUT',
            body: formData 
        });
        
        if (response.ok) {
            alert('Juego actualizado con éxito!');
            document.getElementById('juego-edit-modal').style.display = 'none';
            cargarJuegos();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error desconocido');
        }
    } catch (error) {
        alert('Error al actualizar juego: ' + error.message);
        console.error(error);
    }
}

async function eliminarJuego(id) {
    if (!confirm('¿Estás seguro de eliminar este juego?')) return;
    
    try {
        const response = await fetch(`/api/juegos/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Juego eliminado con éxito!');
            cargarJuegos();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error desconocido');
        }
    } catch (error) {
        alert('Error al eliminar juego: ' + error.message);
        console.error(error);
    }
}


// --- CONSOLAS ---
async function cargarConsolas() {
    try {
        const response = await fetch('/api/consolas/');
        const consolas = await response.json();
        const container = document.getElementById('consolas-container');
        container.innerHTML = '';
        if (consolas.length === 0) {
            container.innerHTML = '<p class="no-results">No hay consolas registradas.</p>';
            return;
        }
        consolas.forEach(consola => {
            const consolaDiv = document.createElement('div');
            consolaDiv.className = 'grid-item';
            consolaDiv.innerHTML = `
                <h3>${consola.nombre}</h3>
                <p><strong>Fabricante:</strong> ${consola.fabricante}</p>
                <p><strong>Año de Lanzamiento:</strong> ${consola.año_lanzamiento || 'N/A'}</p>
                ${consola.imagen ? `<img src="${consola.imagen}" alt="${consola.nombre}" class="item-img">` : '<div class="no-image">No Image</div>'}
                <div class="item-actions">
                    <button class="btn btn-secondary" onclick="abrirModalEditarConsola(${consola.id})">Editar</button>
                    <button class="btn btn-danger" onclick="eliminarConsola(${consola.id})">Eliminar</button>
                </div>
            `;
            container.appendChild(consolaDiv);
        });
    } catch (error) {
        console.error('Error al cargar consolas:', error);
        alert('Error al cargar consolas: ' + error.message);
    }
}

async function crearConsola(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch('/api/consolas/', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            alert('Consola creada con éxito!');
            form.reset();
            document.getElementById('consola-imagen-preview').src = '';
            document.getElementById('consola-imagen-preview').style.display = 'none';
            cargarConsolas();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error desconocido');
        }
    } catch (error) {
        alert('Error al crear consola: ' + error.message);
        console.error(error);
    }
}

let currentEditConsolaId = null;

async function abrirModalEditarConsola(consolaId) {
    currentEditConsolaId = consolaId;
    const modal = document.getElementById('consola-edit-modal');
    const form = document.getElementById('consola-edit-form');
    
    form.reset();
    document.getElementById('edit-consola-imagen-preview').src = '';
    document.getElementById('edit-consola-imagen-preview').style.display = 'none';
    document.getElementById('mantener-consola-imagen-checkbox').checked = false;

    try {
        const response = await fetch(`/api/consolas/?q=&skip=0&limit=1000`);
        const consolas = await response.json();
        const consola = consolas.find(c => c.id === consolaId);

        if (consola) {
            document.getElementById('edit-consola-nombre').value = consola.nombre;
            document.getElementById('edit-consola-fabricante').value = consola.fabricante;
            document.getElementById('edit-consola-anio-lanzamiento').value = consola.año_lanzamiento || '';
            
            const imgPreview = document.getElementById('edit-consola-imagen-preview');
            const mantenerCheckbox = document.getElementById('mantener-consola-imagen-checkbox');

            if (consola.imagen) {
                imgPreview.src = consola.imagen;
                imgPreview.style.display = 'block';
                mantenerCheckbox.checked = true;
            } else {
                imgPreview.style.display = 'none';
                imgPreview.src = '';
                mantenerCheckbox.checked = false;
            }
            modal.style.display = 'block';
        } else {
            alert('Consola no encontrada.');
        }
    } catch (error) {
        alert('Error al cargar datos de la consola para editar: ' + error.message);
        console.error(error);
    }
}

async function actualizarConsola(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData();

    formData.append('nombre', form.elements['edit-consola-nombre'].value);
    formData.append('fabricante', form.elements['edit-consola-fabricante'].value);
    formData.append('año_lanzamiento', form.elements['edit-consola-anio-lanzamiento'].value);
    
    const imagenInput = form.elements['edit-consola-imagen'];
    if (imagenInput.files && imagenInput.files[0]) {
        formData.append('imagen', imagenInput.files[0]);
    } else {
        formData.append('mantener_imagen_existente', form.elements['mantener-consola-imagen-checkbox'].checked ? 'true' : 'false');
    }

    try {
        const response = await fetch(`/api/consolas/${currentEditConsolaId}`, {
            method: 'PUT',
            body: formData
        });
        
        if (response.ok) {
            alert('Consola actualizada con éxito!');
            document.getElementById('consola-edit-modal').style.display = 'none';
            cargarConsolas();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error desconocido');
        }
    } catch (error) {
        alert('Error al actualizar consola: ' + error.message);
        console.error(error);
    }
}

async function eliminarConsola(id) {
    if (!confirm('¿Estás seguro de eliminar esta consola?')) return;
    
    try {
        const response = await fetch(`/api/consolas/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Consola eliminada con éxito!');
            cargarConsolas();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error desconocido');
        }
    } catch (error) {
        alert('Error al eliminar consola: ' + error.message);
        console.error(error);
    }
}


// --- ACCESORIOS ---
async function cargarAccesorios() {
    try {
        const response = await fetch('/api/accesorios/');
        const accesorios = await response.json();
        const container = document.getElementById('accesorios-container');
        container.innerHTML = '';
        if (accesorios.length === 0) {
            container.innerHTML = '<p class="no-results">No hay accesorios registrados.</p>';
            return;
        }
        accesorios.forEach(accesorio => {
            const accesorioDiv = document.createElement('div');
            accesorioDiv.className = 'grid-item';
            accesorioDiv.innerHTML = `
                <h3>${accesorio.nombre}</h3>
                <p><strong>Tipo:</strong> ${accesorio.tipo}</p>
                <p><strong>Compatible con:</strong> ${accesorio.compatible_con || 'N/A'}</p>
                ${accesorio.imagen ? `<img src="${accesorio.imagen}" alt="${accesorio.nombre}" class="item-img">` : '<div class="no-image">No Image</div>'}
                <div class="item-actions">
                    <button class="btn btn-secondary" onclick="abrirModalEditarAccesorio(${accesorio.id})">Editar</button>
                    <button class="btn btn-danger" onclick="eliminarAccesorio(${accesorio.id})">Eliminar</button>
                </div>
            `;
            container.appendChild(accesorioDiv);
        });
    } catch (error) {
        console.error('Error al cargar accesorios:', error);
        alert('Error al cargar accesorios: ' + error.message);
    }
}

async function crearAccesorio(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch('/api/accesorios/', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            alert('Accesorio creado con éxito!');
            form.reset();
            document.getElementById('accesorio-imagen-preview').src = '';
            document.getElementById('accesorio-imagen-preview').style.display = 'none';
            cargarAccesorios();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error desconocido');
        }
    } catch (error) {
        alert('Error al crear accesorio: ' + error.message);
        console.error(error);
    }
}

let currentEditAccesorioId = null;

async function abrirModalEditarAccesorio(accesorioId) {
    currentEditAccesorioId = accesorioId;
    const modal = document.getElementById('accesorio-edit-modal');
    const form = document.getElementById('accesorio-edit-form');
    
    form.reset();
    document.getElementById('edit-accesorio-imagen-preview').src = '';
    document.getElementById('edit-accesorio-imagen-preview').style.display = 'none';
    document.getElementById('mantener-accesorio-imagen-checkbox').checked = false;

    try {
        const response = await fetch(`/api/accesorios/?q=&skip=0&limit=1000`);
        const accesorios = await response.json();
        const accesorio = accesorios.find(a => a.id === accesorioId);

        if (accesorio) {
            document.getElementById('edit-accesorio-nombre').value = accesorio.nombre;
            document.getElementById('edit-accesorio-tipo').value = accesorio.tipo;
            document.getElementById('edit-accesorio-compatible-con').value = accesorio.compatible_con || '';
            
            const imgPreview = document.getElementById('edit-accesorio-imagen-preview');
            const mantenerCheckbox = document.getElementById('mantener-accesorio-imagen-checkbox');

            if (accesorio.imagen) {
                imgPreview.src = accesorio.imagen;
                imgPreview.style.display = 'block';
                mantenerCheckbox.checked = true;
            } else {
                imgPreview.style.display = 'none';
                imgPreview.src = '';
                mantenerCheckbox.checked = false;
            }
            modal.style.display = 'block';
        } else {
            alert('Accesorio no encontrado.');
        }
    } catch (error) {
        alert('Error al cargar datos del accesorio para editar: ' + error.message);
        console.error(error);
    }
}

async function actualizarAccesorio(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData();

    formData.append('nombre', form.elements['edit-accesorio-nombre'].value);
    formData.append('tipo', form.elements['edit-accesorio-tipo'].value);
    formData.append('compatible_con', form.elements['edit-accesorio-compatible-con'].value);
    
    const imagenInput = form.elements['edit-accesorio-imagen'];
    if (imagenInput.files && imagenInput.files[0]) {
        formData.append('imagen', imagenInput.files[0]);
    } else {
        formData.append('mantener_imagen_existente', form.elements['mantener-accesorio-imagen-checkbox'].checked ? 'true' : 'false');
    }

    try {
        const response = await fetch(`/api/accesorios/${currentEditAccesorioId}`, {
            method: 'PUT',
            body: formData
        });
        
        if (response.ok) {
            alert('Accesorio actualizado con éxito!');
            document.getElementById('accesorio-edit-modal').style.display = 'none';
            cargarAccesorios();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error desconocido');
        }
    } catch (error) {
        alert('Error al actualizar accesorio: ' + error.message);
        console.error(error);
    }
}

async function eliminarAccesorio(id) {
    if (!confirm('¿Estás seguro de eliminar este accesorio?')) return;
    
    try {
        const response = await fetch(`/api/accesorios/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Accesorio eliminado con éxito!');
            cargarAccesorios();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error desconocido');
        }
    } catch (error) {
        alert('Error al eliminar accesorio: ' + error.message);
        console.error(error);
    }
}

// --- COMPARACIONES (sin cambios en JS, ya que no manejan archivos) ---
async function cargarComparaciones() {
    try {
        const response = await fetch('/api/comparaciones/');
        const comparaciones = await response.json();
        const container = document.getElementById('comparaciones-container');
        container.innerHTML = '';
        if (comparaciones.length === 0) {
            container.innerHTML = '<p class="no-results">No hay comparaciones registradas.</p>';
            return;
        }
        comparaciones.forEach(comp => {
            const compDiv = document.createElement('div');
            compDiv.className = 'comparacion-item';
            compDiv.innerHTML = `
                <div class="comparacion-header">
                    <h3 class="comparacion-title">${comp.nombre}</h3>
                    <button class="btn btn-danger btn-sm" onclick="eliminarComparacion(${comp.id})">Eliminar</button>
                </div>
                <p><strong>Juego:</strong> ${comp.juego_nombre} (${comp.juego_genero}, ${comp.juego_año})</p>
                <p><strong>Consola:</strong> ${comp.consola_nombre} (${comp.consola_fabricante}, ${comp.consola_año_lanzamiento})</p>
                ${comp.accesorio_nombre ? `<p><strong>Accesorio:</strong> ${comp.accesorio_nombre} (${comp.accesorio_tipo})</p>` : ''}
                ${comp.notas ? `<p><strong>Notas:</strong> ${comp.notas}</p>` : ''}
                <div class="comparison-images">
                    ${comp.juego_imagen ? `<img src="${comp.juego_imagen}" alt="Imagen de ${comp.juego_nombre}" class="comparison-img">` : '<div class="no-image-small">No Image</div>'}
                    ${comp.consola_imagen ? `<img src="${comp.consola_imagen}" alt="Imagen de ${comp.consola_nombre}" class="comparison-img">` : '<div class="no-image-small">No Image</div>'}
                    ${comp.accesorio_imagen ? `<img src="${comp.accesorio_imagen}" alt="Imagen de ${comp.accesorio_nombre}" class="comparison-img">` : ''}
                </div>
            `;
            container.appendChild(compDiv);
        });
    } catch (error) {
        console.error('Error al cargar comparaciones:', error);
        alert('Error al cargar comparaciones: ' + error.message);
    }
}

async function crearComparacion(event) {
    event.preventDefault();
    const form = event.target;
    const nombre = form.elements['comparacion-nombre'].value;
    const juego_id = form.elements['comparacion-juego'].value;
    const consola_id = form.elements['comparacion-consola'].value;
    const accesorio_id = form.elements['comparacion-accesorio'].value || null; 
    const notas = form.elements['comparacion-notas'].value;

    try {
        const response = await fetch('/api/comparaciones/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nombre: nombre,
                juego_id: parseInt(juego_id),
                consola_id: parseInt(consola_id),
                accesorio_id: accesorio_id ? parseInt(accesorio_id) : null,
                notas: notas
            })
        });
        
        if (response.ok) {
            alert('Comparación creada con éxito!');
            form.reset();
            cargarComparaciones();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error desconocido');
        }
    } catch (error) {
        alert('Error al crear comparación: ' + error.message);
        console.error(error);
    }
}

async function eliminarComparacion(id) {
    if (!confirm('¿Estás seguro de eliminar esta comparación?')) return;
    
    try {
        const response = await fetch(`/api/comparaciones/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Comparación eliminada con éxito!');
            cargarComparaciones();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error desconocido');
        }
    } catch (error) {
        alert('Error al eliminar comparación: ' + error.message);
        console.error(error);
    }
}

// --- Funciones para manejar la lógica de modals y carga inicial ---

// General function to open/close modals (make sure these exist in your HTML)
function setupModal(modalId, openBtnId, closeClass) {
    const modal = document.getElementById(modalId);
    const openBtn = document.getElementById(openBtnId);
    const closeSpan = modal.querySelector(`.${closeClass}`);

    if (openBtn) {
        openBtn.onclick = function() {
            modal.style.display = 'block';
        }
    }

    if (closeSpan) {
        closeSpan.onclick = function() {
            modal.style.display = 'none';
        }
    }

    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
}

// Previsualización de imágenes para formularios de creación y edición
function setupImagePreview(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);

    if (input && preview) {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }
                reader.readAsDataURL(file);
            } else {
                preview.src = '';
                preview.style.display = 'none';
            }
        });
    }
}

// --- Carga inicial de datos y listeners ---
document.addEventListener('DOMContentLoaded', () => {
    // Cargar datos según la página actual
    const path = window.location.pathname;

    if (path === '/') { 
        cargarJuegos();
        setupImagePreview('juego-imagen', 'juego-imagen-preview');
        setupImagePreview('edit-juego-imagen', 'edit-juego-imagen-preview');
        setupModal('juego-edit-modal', '', 'close'); 
        
        const juegoForm = document.getElementById('juego-form');
        if (juegoForm) juegoForm.addEventListener('submit', crearJuego);
        
        const juegoEditForm = document.getElementById('juego-edit-form');
        if (juegoEditForm) juegoEditForm.addEventListener('submit', actualizarJuego);

    } else if (path === '/consolas') {
        cargarConsolas();
        setupImagePreview('consola-imagen', 'consola-imagen-preview');
        setupImagePreview('edit-consola-imagen', 'edit-consola-imagen-preview');
        setupModal('consola-edit-modal', '', 'close');
        
        const consolaForm = document.getElementById('consola-form');
        if (consolaForm) consolaForm.addEventListener('submit', crearConsola);

        const consolaEditForm = document.getElementById('consola-edit-form');
        if (consolaEditForm) consolaEditForm.addEventListener('submit', actualizarConsola);

    } else if (path === '/accesorios') {
        cargarAccesorios();
        setupImagePreview('accesorio-imagen', 'accesorio-imagen-preview');
        setupImagePreview('edit-accesorio-imagen', 'edit-accesorio-imagen-preview');
        setupModal('accesorio-edit-modal', '', 'close');

        const accesorioForm = document.getElementById('accesorio-form');
        if (accesorioForm) accesorioForm.addEventListener('submit', crearAccesorio);
        
        const accesorioEditForm = document.getElementById('accesorio-edit-form');
        if (accesorioEditForm) accesorioEditForm.addEventListener('submit', actualizarAccesorio);

    } else if (path === '/comparaciones') {
        cargarComparaciones();
        cargarJuegosParaSelect(); 
        cargarConsolasParaSelect(); 
        cargarAccesoriosParaSelect(); 

        setupModal('comparacion-modal', 'nueva-comparacion-btn', 'close');
        
        const nuevaComparacionForm = document.getElementById('nueva-comparacion-form');
        if (nuevaComparacionForm) nuevaComparacionForm.addEventListener('submit', crearComparacion);
    }

    // Lógica para la búsqueda rápida (presente en todas las páginas, típicamente en index.html)
    const searchInput = document.getElementById('search-query');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') buscarRapida();
        });
    }
});

// Funciones auxiliares para cargar selects en el modal de comparaciones (si no las tienes)
async function cargarJuegosParaSelect() {
    try {
        const response = await fetch('/api/juegos/');
        const juegos = await response.json();
        const select = document.getElementById('comparacion-juego');
        select.innerHTML = '<option value="">Selecciona un Juego</option>';
        juegos.forEach(juego => {
            const option = document.createElement('option');
            option.value = juego.id;
            option.textContent = juego.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar juegos para select:', error);
    }
}

async function cargarConsolasParaSelect() {
    try {
        const response = await fetch('/api/consolas/');
        const consolas = await response.json();
        const select = document.getElementById('comparacion-consola');
        select.innerHTML = '<option value="">Selecciona una Consola</option>';
        consolas.forEach(consola => {
            const option = document.createElement('option');
            option.value = consola.id;
            option.textContent = consola.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar consolas para select:', error);
    }
}

async function cargarAccesoriosParaSelect() {
    try {
        const response = await fetch('/api/accesorios/');
        const accesorios = await response.json();
        const select = document.getElementById('comparacion-accesorio');
        select.innerHTML = '<option value="">Selecciona un Accesorio (Opcional)</option>';
        accesorios.forEach(accesorio => {
            const option = document.createElement('option');
            option.value = accesorio.id;
            option.textContent = accesorio.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar accesorios para select:', error);
    }
}