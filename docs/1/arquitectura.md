# Arquitectura — Ejercicio 1

## Visión general

El ejercicio 1 descompone la aplicación monolítica de la práctica 4 (ejercicio
2) en dos componentes desplegables por separado y una infraestructura común
basada en Docker Compose:

```
┌───────────────┐       HTTP/JSON        ┌──────────────────┐      SQL       ┌───────────┐
│  Navegador    │ ─────────────────────▶ │  Aplicación web  │ ─────────────▶ │           │
│  (cliente)    │ ◀───────────────────── │   Flask :5001    │                │           │
└───────────────┘    HTML + fetch JSON   │  (frontend HTML) │                │           │
                                         └─────────┬────────┘                │  MariaDB  │
                                                   │ requests                │   :3306   │
                                                   ▼                         │           │
                                         ┌──────────────────┐      SQL       │           │
                                         │  Microservicio   │ ─────────────▶ │           │
                                         │ Flask-RESTful    │                └───────────┘
                                         │     :5101        │
                                         └──────────────────┘
```

## Componentes

### Aplicación web (`src/1/web/`)

Aplicación Flask con plantillas HTML y JavaScript vanilla del lado del
cliente. No accede directamente a la base de datos: delega toda la
persistencia y la validación de credenciales en el microservicio.

- Mantiene la sesión del usuario autenticado en la sesión de Flask
  (`flask.session`), reutilizando el modelo de control de acceso de la
  práctica 4. La sustitución de este control por JWT se realizará en el
  ejercicio 3.
- Expone al navegador los endpoints `/api/tareas` que internamente reenvían
  la petición al microservicio con `requests`. Este paso intermedio existe
  para aplicar las reglas de visibilidad (admin ve todo, usuario normal solo
  lo suyo) sin exponer directamente el microservicio al navegador en este
  ejercicio.

### Microservicio de datos (`src/1/api/`)

Servicio REST construido con Flask-RESTful y Flask-SQLAlchemy. Expone
operaciones públicas de creación, consulta, edición y eliminación sobre los
recursos `users` y `tareas`, más un endpoint `POST /api/auth` para validar
credenciales.

- Es el único componente que habla con MariaDB.
- Se activa CORS (Flask-CORS) para que, si en un futuro fuera consumido
  directamente desde el navegador, no haya bloqueos por origen cruzado.
- La entidad `Tarea` mantiene una clave foránea `owner_id` hacia `User`,
  preservando la lógica de tareas asociadas a cada usuario.

### Infraestructura (`p5/infra/`)

`docker-compose.yml` con MariaDB 11 y phpMyAdmin, reutilizando el enfoque de
la práctica 4. Un script `initdb/01-create-databases.sh` crea de forma
automática la base de datos `p5_ej1_tareas` y concede privilegios al usuario
de aplicación.

## Flujo de una petición

1. El navegador envía el formulario de login (`POST /login`) a la aplicación
   web.
2. La aplicación web llama a `POST http://127.0.0.1:5101/api/auth` usando
   `requests` y recibe el JSON con los datos del usuario.
3. Si las credenciales son correctas, la web guarda el usuario en la sesión
   y redirige al panel.
4. El panel carga sus tareas con `fetch('/api/tareas')` hacia la propia web;
   la web añade el filtro `owner_id` cuando procede y reenvía la consulta al
   microservicio.
5. El microservicio consulta MariaDB, serializa los resultados con el método
   `to_dict()` y los devuelve como JSON.

## Puertos utilizados en desarrollo local

- `3306`: MariaDB.
- `8080`: phpMyAdmin.
- `5101`: microservicio de datos.
- `5001`: aplicación web.

## Relación con la práctica 4

La interfaz de usuario, la lógica de autenticación con sesión y la
diferenciación entre administrador y usuario normal se conservan exactamente
como en el ejercicio 2 de la práctica 4. El único cambio estructural es la
extracción del acceso a datos a un microservicio independiente: los modelos
SQLAlchemy y el servicio de autenticación han pasado de `backend/` a
`api/`, y el frontend ha dejado de depender de `flask_login` para depender
del microservicio a través de `api_client`.
