# GameHub - Sistema de Gestión de Videojuegos

Un sistema completo de gestión de videojuegos desarrollado con Flask, SQLite y una interfaz web moderna con temática gaming.

## 🎮 Características

- **CRUD Completo**: Gestión de juegos, consolas y accesorios
- **API REST**: Endpoints completos para todas las funcionalidades
- **Interfaz Web**: Dashboard moderno con temática gaming
- **Búsqueda Avanzada**: Búsqueda global y filtros especializados
- **Comparación**: Comparar productos lado a lado
- **Estadísticas**: Análisis y reportes del sistema
- **Responsive**: Optimizado para desktop y móviles
- **APIs Externas**: Integración con APIs de videojuegos

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.8 o superior
- Visual Studio Code
- Git (opcional)

### Pasos de Instalación

1. **Extraer el proyecto**
   ```bash
   # Extraer el archivo ZIP en tu directorio preferido
   # Ejemplo: C:\Proyectos\GameHub\
   ```

2. **Abrir en Visual Studio Code**
   ```bash
   # Abrir Visual Studio Code
   # File > Open Folder > Seleccionar la carpeta del proyecto
   ```

3. **Crear entorno virtual**
   ```bash
   # En la terminal de VS Code (Terminal > New Terminal)
   python -m venv venv
   
   # Activar el entorno virtual
   # En Windows:
   venv\Scripts\activate
   
   # En macOS/Linux:
   source venv/bin/activate
   ```

4. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecutar el sistema**
   ```bash
   python server_test.py
   ```

6. **Acceder al sistema**
   - Interfaz Web: http://localhost:5002/
   - API REST: http://localhost:5002/api/

## 📁 Estructura del Proyecto

```
videojuegos_system/
├── src/
│   ├── models/           # Modelos de base de datos
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── juegos.py
│   │   ├── consolas.py
│   │   ├── accesorios.py
│   │   └── historial.py
│   ├── services/         # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── crud_service.py
│   │   ├── juegos_service.py
│   │   ├── consolas_service.py
│   │   ├── accesorios_service.py
│   │   ├── catalogo_service.py
│   │   └── comparacion_service.py
│   ├── routes/           # Endpoints de la API
│   │   ├── __init__.py
│   │   ├── juegos.py
│   │   ├── consolas.py
│   │   ├── accesorios.py
│   │   ├── catalogo.py
│   │   ├── comparacion.py
│   │   └── web.py
│   ├── api/              # Clientes de APIs externas
│   │   ├── __init__.py
│   │   ├── rawg_client.py
│   │   ├── igdb_client.py
│   │   ├── mock_client.py
│   │   └── api_manager.py
│   ├── templates/        # Templates HTML
│   │   ├── base.html
│   │   └── index.html
│   ├── static/           # Archivos estáticos
│   │   ├── css/
│   │   │   ├── base.css
│   │   │   └── components.css
│   │   ├── js/
│   │   │   ├── base.js
│   │   │   └── api.js
│   │   └── images/
│   └── utils/            # Utilidades
├── instance/             # Base de datos SQLite
├── server_test.py        # Servidor principal
├── requirements.txt      # Dependencias
└── README.md            # Este archivo
```

## 🎯 Funcionalidades Principales

### 1. Dashboard Principal
- Estadísticas en tiempo real
- Productos destacados
- Acciones rápidas
- Navegación intuitiva

### 2. Gestión de Juegos
- Crear, editar, eliminar juegos
- Búsqueda por nombre, género, plataforma
- Filtros avanzados
- Juegos populares y recientes

### 3. Gestión de Consolas
- CRUD completo de consolas
- Filtros por fabricante, tipo, generación
- Estadísticas de consolas

### 4. Gestión de Accesorios
- Administración de accesorios gaming
- Filtros por tipo, fabricante, compatibilidad
- Control de inventario

### 5. Catálogo Unificado
- Vista global de todos los productos
- Búsqueda global avanzada
- Filtros por categoría
- Productos destacados

### 6. Sistema de Comparación
- Comparar hasta 5 productos
- Comparación lado a lado
- Análisis detallado de características

## 🔧 API REST

### Endpoints Principales

#### Juegos
- `GET /api/juegos/` - Listar juegos
- `POST /api/juegos/` - Crear juego
- `GET /api/juegos/{id}` - Obtener juego
- `PUT /api/juegos/{id}` - Actualizar juego
- `DELETE /api/juegos/{id}` - Eliminar juego
- `GET /api/juegos/buscar?q=termino` - Buscar juegos
- `GET /api/juegos/populares` - Juegos populares
- `GET /api/juegos/estadisticas` - Estadísticas

#### Consolas
- `GET /api/consolas/` - Listar consolas
- `POST /api/consolas/` - Crear consola
- `GET /api/consolas/{id}` - Obtener consola
- `PUT /api/consolas/{id}` - Actualizar consola
- `DELETE /api/consolas/{id}` - Eliminar consola
- `GET /api/consolas/fabricantes/{fabricante}` - Por fabricante

#### Accesorios
- `GET /api/accesorios/` - Listar accesorios
- `POST /api/accesorios/` - Crear accesorio
- `GET /api/accesorios/tipos/{tipo}` - Por tipo
- `GET /api/accesorios/compatibilidad/{compatibilidad}` - Por compatibilidad

#### Catálogo
- `GET /api/catalogo/` - Resumen del catálogo
- `GET /api/catalogo/buscar?q=termino` - Búsqueda global
- `GET /api/catalogo/destacados` - Productos destacados

#### Comparación
- `POST /api/comparacion/juegos` - Comparar juegos
- `POST /api/comparacion/consolas` - Comparar consolas
- `POST /api/comparacion/accesorios` - Comparar accesorios

## 🎨 Interfaz Web

### Características del Diseño
- **Temática Gaming**: Colores neón, efectos visuales, tipografía futurista
- **Responsive**: Adaptable a todos los dispositivos
- **Interactiva**: Animaciones, hover effects, transiciones suaves
- **Moderna**: Diseño limpio y profesional
- **Accesible**: Navegación intuitiva y clara

### Páginas Principales
- **Dashboard** (`/`) - Página principal con estadísticas
- **Juegos** (`/juegos`) - Gestión de juegos
- **Consolas** (`/consolas`) - Gestión de consolas
- **Accesorios** (`/accesorios`) - Gestión de accesorios
- **Catálogo** (`/catalogo`) - Vista unificada
- **Comparación** (`/comparacion`) - Comparar productos
- **Búsqueda** (`/buscar`) - Búsqueda global

## 🛠️ Desarrollo

### Configuración para Desarrollo

1. **Activar modo debug**
   ```python
   # En server_test.py, la línea final:
   app.run(host='0.0.0.0', port=5002, debug=True)
   ```

2. **Variables de entorno** (opcional)
   ```bash
   # Crear archivo .env
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=tu-clave-secreta
   ```

3. **Extensiones recomendadas para VS Code**
   - Python
   - Flask Snippets
   - HTML CSS Support
   - JavaScript (ES6) code snippets
   - SQLite Viewer

### Estructura de Base de Datos

El sistema utiliza SQLite con las siguientes tablas:
- `juegos` - Información de videojuegos
- `consolas` - Datos de consolas
- `accesorios` - Accesorios gaming
- `historial_acciones` - Log de todas las acciones del sistema

## 🚀 Despliegue

Para desplegar en producción:

1. **Cambiar configuración**
   ```python
   app.config['DEBUG'] = False
   app.config['SECRET_KEY'] = 'clave-secreta-segura'
   ```

2. **Usar servidor WSGI**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 server_test:app
   ```

## 📝 Notas Importantes

- La base de datos se crea automáticamente al ejecutar el servidor
- Los datos de prueba se generan usando APIs simuladas
- El sistema incluye validaciones y manejo de errores
- Todas las operaciones se registran en el historial
- La interfaz es completamente funcional sin JavaScript (progressive enhancement)

## 🐛 Solución de Problemas

### Error: ModuleNotFoundError
```bash
# Asegúrate de que el entorno virtual esté activado
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: Puerto en uso
```bash
# Cambiar puerto en server_test.py línea final:
app.run(host='0.0.0.0', port=5003, debug=True)  # Usar puerto 5003
```

### Error: Base de datos
```bash
# Eliminar base de datos y reiniciar
rm instance/videojuegos.db
python server_test.py
```

## 📞 Soporte

Para reportar problemas o sugerencias:
- Revisar la consola de VS Code para errores
- Verificar que todas las dependencias estén instaladas
- Comprobar que el puerto 5002 esté disponible

## 🎮 ¡Disfruta GameHub!

El sistema está listo para usar. Accede a http://localhost:5002/ y comienza a gestionar tu colección de videojuegos.

---

**Desarrollado con ❤️ para gamers por gamers**

