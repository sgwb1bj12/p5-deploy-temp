# Ejercicio 1 — Microservicio de datos y usuarios

Separación de la aplicación monolítica de la práctica 4 (ejercicio 2) en:

- `web/`: aplicación Flask con interfaz HTML para el usuario final. Consume la
  API del microservicio desde el servidor mediante el paquete `requests`.
- `api/`: microservicio de datos construido con Flask-RESTful y
  Flask-SQLAlchemy, responsable del acceso a MariaDB.

## Requisitos

Dependencias de Python compartidas por los dos componentes:

```bash
pip3 install -r requirements.txt
```

Además es necesario tener arriba la infraestructura común de Docker (MariaDB +
phpMyAdmin) definida en `p5/infra/`.

## Arranque en desarrollo local

1. Levantar MariaDB y phpMyAdmin:

   ```bash
   cd ../../infra
   docker compose --env-file .env -f docker-compose.yml up -d
   ```

2. Arrancar el microservicio de datos (puerto `5101`):

   ```bash
   cd api
   python3 app.py
   ```

3. Arrancar la aplicación web (puerto `5001`) en otra terminal:

   ```bash
   cd web
   python3 app.py
   ```

4. Abrir `http://127.0.0.1:5001` en el navegador. Credenciales de prueba:
   `admin/admin` (administrador) o `user/user` (usuario normal).

## Endpoints de la API

| Método | Ruta                    | Descripción                                    |
| ------ | ----------------------- | ---------------------------------------------- |
| GET    | `/api/users`            | Listado de usuarios.                           |
| POST   | `/api/users`            | Alta de usuario (`username`, `password`, `role`). |
| GET    | `/api/users/<id>`       | Detalle de un usuario.                         |
| DELETE | `/api/users/<id>`       | Baja de un usuario.                            |
| POST   | `/api/auth`             | Autenticación (`username`, `password`).        |
| GET    | `/api/tareas`           | Listado de tareas. Filtro `?owner_id=`.        |
| POST   | `/api/tareas`           | Alta de tarea (`title`, `owner_id`).           |
| GET    | `/api/tareas/<id>`      | Detalle de una tarea.                          |
| PATCH  | `/api/tareas/<id>`      | Modificación parcial (`completed`, `title`).   |
| DELETE | `/api/tareas/<id>`      | Baja de una tarea.                             |

## Variables de entorno

El microservicio acepta configuración vía variables de entorno:

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.

La aplicación web acepta:

- `API_BASE_URL` (por defecto `http://127.0.0.1:5101`).
