# Despliegue en PythonAnywhere

## URLs públicas

> Rellenar con las URLs reales tras el despliegue.

| Componente | URL |
|------------|-----|
| Web SVAIA  | `https://___.pythonanywhere.com/` |
| API datos  | `https://___.pythonanywhere.com/` |
| Chat       | `https://___.pythonanywhere.com/` |

## Separación en producción

PythonAnywhere en plan gratuito solo permite una web app por cuenta. Para
mantener la separación arquitectónica de la práctica, cada microservicio
vive en una cuenta distinta o en una app independiente dentro de la misma
cuenta si el plan lo permite. La web consume a los otros dos a través de
sus URLs públicas, no por `localhost`.

## Configuración que cambia respecto a local

### Variables de entorno por componente

**Web (`src/2/web`)**
- `API_BASE_URL=https://<api>.pythonanywhere.com`
- `CHAT_BASE_URL=https://<chat>.pythonanywhere.com`
- `SECRET_KEY=<valor fuerte>`

**API (`src/2/api`)**
- `DB_HOST=<host MySQL de PythonAnywhere>`
- `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `SECRET_KEY=<mismo valor que el chat>`

**Chat (`src/2/chat`)**
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` (mismas que la API)
- `SECRET_KEY=<mismo valor que la API>` — si no coinciden, el chat no
  valida los tokens emitidos por la API.
- `CORS_ORIGINS=https://<web>.pythonanywhere.com` — debe ser el origen
  público exacto de la web desplegada.

### Base de datos

En local MariaDB corre en Docker. En PythonAnywhere se usa el servicio
MySQL que ofrece la plataforma. El esquema se crea desde la consola Bash
importando el dump o dejando que `db.create_all()` lo genere al arrancar
la API por primera vez.

### CORS en producción

El punto más fácil de pasar por alto. El chat debe permitir como origen
la URL pública de la web, no `localhost`. Sin eso, la app desplegada
carga pero el chat falla en el navegador con error CORS.

### WSGI

Cada web app en PythonAnywhere usa un archivo WSGI propio que importa
`app` desde `app.py`:

```python
import sys, os
path = "/home/<usuario>/src/2/web"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["API_BASE_URL"] = "https://..."
os.environ["CHAT_BASE_URL"] = "https://..."
os.environ["SECRET_KEY"] = "..."

from app import app as application
```

Y equivalente para `api` y `chat` con sus rutas y variables.

## Checklist de verificación

Tras desplegar:

1. `GET` a la URL de la web carga la home sin errores 500.
2. Login con `admin/admin` redirige al panel y la cabecera muestra el
   usuario.
3. El panel lista los mensajes previos (si los hay) sin errores de
   conexión contra la API.
4. Chat: enviar un mensaje devuelve respuesta. En DevTools se ve el
   `POST` al dominio del chat con status 200 y cabecera CORS correcta.
5. Cerrar sesión y volver a `/chat` redirige al login (sin token en
   sesión).
6. Un `curl` directo a `GET /api/mensajes` sin token devuelve 401.
