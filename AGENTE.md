# AGENTE.md

## Estructura del Proyecto

Este proyecto es una aplicación Django basada en el starter "Django AdminLTE". A continuación se detalla la estructura principal del proyecto:

- **`apps/`**: Contiene las distintas aplicaciones (módulos) de Django que conforman el sistema.
  - `pages/`: Vistas y modelos para las páginas principales, como `Product`.
  - `core/`: Configuración base y utilidades centrales.
  - `dyn_dt/`: Módulo para la generación dinámica de DataTables.
  - `dyn_api/`: Módulo para exponer APIs dinámicas usando Django REST Framework.
  - `charts/`: Aplicación para visualización de gráficos utilizando ApexCharts.
- **`config/`**: Contiene la configuración global del proyecto Django.
  - `settings.py`: Configuraciones principales (Base de datos, Middlewares, Apps Instaladas, etc.).
  - `urls.py`: Enrutamiento principal del proyecto.
  - `wsgi.py` / `asgi.py`: Puntos de entrada para servidores web.
- **`templates/`**: Almacena las plantillas HTML (arquitectura MVT) utilizadas para renderizar la interfaz de usuario.
  - Contiene subdirectorios como `core`, `pages`, `layouts`, entre otros, basados en el diseño de AdminLTE.
- **`static/`**: Archivos estáticos como CSS, JavaScript e imágenes.
- **`manage.py`**: Script principal de utilidad de línea de comandos de Django.
- **Archivos de despliegue**: `Dockerfile`, `docker-compose.yml`, `render.yaml`, `build.sh`, `deploy.sh` que facilitan el despliegue mediante contenedores o plataformas en la nube como Render.

---

## Conexión a Base de Datos PostgreSQL

El proyecto soporta de manera nativa la conexión a PostgreSQL a través de variables de entorno configuradas en el archivo `.env` o en el entorno de despliegue.

En el archivo `config/settings.py`, la configuración de la base de datos se evalúa de la siguiente manera:

```python
DB_ENGINE   = os.getenv('DB_ENGINE'   , None)
DB_USERNAME = os.getenv('DB_USERNAME' , None)
DB_PASS     = os.getenv('DB_PASS'     , None)
DB_HOST     = os.getenv('DB_HOST'     , None)
DB_PORT     = os.getenv('DB_PORT'     , None)
DB_NAME     = os.getenv('DB_NAME'     , None)

if DB_ENGINE and DB_NAME and DB_USERNAME:
    DATABASES = {
      'default': {
        'ENGINE'  : 'django.db.backends.' + DB_ENGINE,
        'NAME'    : DB_NAME,
        'USER'    : DB_USERNAME,
        'PASSWORD': DB_PASS,
        'HOST'    : DB_HOST,
        'PORT'    : DB_PORT,
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }
```

Para conectar a una base de datos PostgreSQL, asegúrate de definir las siguientes variables de entorno:

- `DB_ENGINE=postgresql`
- `DB_NAME=<nombre_de_tu_base_de_datos>`
- `DB_USERNAME=<usuario_postgres>`
- `DB_PASS=<contraseña_postgres>`
- `DB_HOST=<host_de_la_bd>` (por ejemplo: `localhost` o el endpoint de AWS/Render)
- `DB_PORT=5432`

*Nota: Por defecto, si estas variables no están configuradas, el proyecto utilizará SQLite3.*

---

## Arquitectura MVT (Modelo-Vista-Plantilla)

Este proyecto sigue estrictamente el patrón de diseño MVT de Django:

### Modelo (Model)
Los modelos se encuentran dentro del archivo `models.py` de cada aplicación en `apps/`.
- Definen la estructura de la base de datos usando el ORM de Django.
- Ejemplo: En `apps/pages/models.py` se define el modelo `Product`, que representa un producto con campos `id`, `name`, `info` y `price`.

### Vista (View)
Las vistas gestionan la lógica de negocio y se ubican en los archivos `views.py` o mediante el enrutamiento y configuraciones dinámicas (`urls.py`).
- Reciben las solicitudes HTTP, interactúan con los modelos para recuperar o guardar datos y deciden qué plantilla renderizar.
- El proyecto también utiliza características avanzadas, como `dyn_api` (Django REST Framework) para proporcionar endpoints de API y `dyn_dt` para las tablas de datos, separando la lógica para una mejor mantenibilidad.

### Plantilla (Template)
Las plantillas manejan la capa de presentación y se encuentran principalmente en el directorio `templates/`.
- Utilizan el motor de plantillas de Django para inyectar datos en páginas HTML predefinidas.
- La interfaz está construida con **AdminLTE** y **Bootstrap**, permitiendo diseños responsivos y estéticamente atractivos sin acoplar la lógica de backend. En `apps/pages/views.py`, la vista `index` por ejemplo renderiza el template `core/base.html`.
