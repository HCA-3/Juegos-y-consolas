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
function mostrarResultados(resultados) {
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
        section.className = 'result-section';
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
            
            if (item.imagen) {
                html += `<img src="${item.imagen}" alt="${item.nombre}" class="minecraft-img">`;
            }
            
            itemElement.innerHTML = html;
            section.appendChild(itemElement);
        });
        
        container.appendChild(section);
    }
}

// Event listeners para búsqueda al presionar Enter
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('search-query').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') buscarRapida();
    });
});