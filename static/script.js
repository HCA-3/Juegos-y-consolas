// Mostrar sección seleccionada
function mostrarSeccion(seccion) {
    document.querySelectorAll('.minecraft-section').forEach(el => {
        el.style.display = 'none';
    });
    document.getElementById(`${seccion}-section`).style.display = 'block';
}

// Cargar datos al iniciar
document.addEventListener('DOMContentLoaded', async () => {
    // Cargar consolas para el formulario de accesorios
    const consolas = await fetch('/api/consolas').then(res => res.json());
    const consolasContainer = document.getElementById('consolas-compatibles');
    
    consolas.forEach(consola => {
        const label = document.createElement('label');
        label.className = 'minecraft-checkbox';
        label.innerHTML = `
            <input type="checkbox" name="consolas_compatibles" value="${consola.id}">
            ${consola.nombre}
        `;
        consolasContainer.appendChild(label);
    });
    
    // Cargar juegos y consolas para compatibilidad
    const [juegos, todasConsolas, accesorios] = await Promise.all([
        fetch('/api/juegos').then(res => res.json()),
        fetch('/api/consolas').then(res => res.json()),
        fetch('/api/accesorios').then(res => res.json())
    ]);
    
    // Llenar selects de compatibilidad
    const juegoSelect = document.getElementById('juego-compatibilidad');
    const consolaSelect = document.getElementById('consola-compatibilidad');
    const accesorioSelect = document.getElementById('accesorio-compatibilidad');
    
    juegos.forEach(juego => {
        const option = document.createElement('option');
        option.value = juego.id;
        option.textContent = juego.nombre;
        juegoSelect.appendChild(option);
    });
    
    todasConsolas.forEach(consola => {
        const option = document.createElement('option');
        option.value = consola.id;
        option.textContent = consola.nombre;
        consolaSelect.appendChild(option);
    });
    
    accesorios.forEach(accesorio => {
        const option = document.createElement('option');
        option.value = accesorio.id;
        option.textContent = accesorio.nombre;
        accesorioSelect.appendChild(option);
    });
    
    // Configurar formularios
    document.getElementById('juego-form').addEventListener('submit', crearJuego);
    document.getElementById('consola-form').addEventListener('submit', crearConsola);
    document.getElementById('accesorio-form').addEventListener('submit', crearAccesorio);
    document.getElementById('compatibilidad-form').addEventListener('submit', crearCompatibilidad);
});

// Funciones para crear elementos
async function crearJuego(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/api/juegos', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            alert('Juego creado con éxito!');
            location.reload();
        }
    } catch (error) {
        alert('Error al crear juego: ' + error.message);
    }
}

async function crearConsola(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/api/consolas', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            alert('Consola creada con éxito!');
            location.reload();
        }
    } catch (error) {
        alert('Error al crear consola: ' + error.message);
    }
}

async function crearAccesorio(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    // Agregar consolas compatibles
    const checkboxes = document.querySelectorAll('input[name="consolas_compatibles"]:checked');
    const consolasCompatibles = Array.from(checkboxes).map(cb => cb.value).join(',');
    formData.append('compatible_con', consolasCompatibles);
    
    try {
        const response = await fetch('/api/accesorios', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            alert('Accesorio creado con éxito!');
            location.reload();
        }
    } catch (error) {
        alert('Error al crear accesorio: ' + error.message);
    }
}

async function crearCompatibilidad(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/compatibilidad', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('Compatibilidad establecida con éxito!');
            location.reload();
        }
    } catch (error) {
        alert('Error al establecer compatibilidad: ' + error.message);
    }
}