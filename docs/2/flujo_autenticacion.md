# Flujo de autenticación y autorización

## Login

El usuario entra credenciales en `/login`. Flujo paso a paso:

1. El navegador hace `POST /login` a la web con el formulario.
2. En `src/2/web/controllers/auth_controller.py`, `login()` llama a
   `api_client.autenticar(username, password)`.
3. Ese cliente hace `POST http://127.0.0.1:5202/api/auth/login` con el
   JSON de credenciales.
4. La API (`AuthResource.post`) llama a `guard.authenticate(...)` de
   Flask-Praetorian. Si las credenciales son válidas, genera el token con
   `guard.encode_jwt_token(user)` y responde:
   ```json
   {
     "access_token": "eyJhbGc...",
     "token_type": "Bearer",
     "user": {"id": 1, "username": "admin", "role": "admin"}
   }
   ```
5. La web guarda `access_token` y `user` en la sesión Flask y redirige a
   `/panel`.
6. Si la API responde 401, `api_client.autenticar` devuelve `None` y la
   web pinta "Credenciales no válidas".

## Acceso a recurso protegido desde el servidor (web ↔ API)

Ejemplo: listar el historial en el panel.

1. `/panel` lee `session["access_token"]`.
2. Llama a `api_client.listar_mensajes(token)`, que hace
   `GET /api/mensajes` con `Authorization: Bearer <token>`.
3. La API ejecuta el decorador `@flask_praetorian.auth_required`. Si el
   token es inválido o falta, responde 401 antes de entrar al handler.
4. Si es válido, el handler filtra por `user_id` salvo que el rol sea
   admin.
5. La API devuelve los mensajes; la web los pinta en la plantilla.

## Acceso a recurso protegido desde el navegador (navegador ↔ chat)

Ejemplo: enviar un mensaje al chat.

1. `chat.html` inyecta el token en `window.SVAIA_TOKEN` desde la sesión.
2. El usuario escribe y `chat.js` dispara:
   ```js
   fetch(window.SVAIA_CHAT_URL, {
     method: "POST",
     headers: {
       "Content-Type": "application/json",
       "Authorization": "Bearer " + window.SVAIA_TOKEN
     },
     body: JSON.stringify({ message })
   });
   ```
3. El navegador hace preflight `OPTIONS /api/chat` contra `:5203`. El chat
   responde con las cabeceras CORS correctas (ver `cors.md`).
4. El navegador manda el `POST`. Flask-Praetorian valida el token; si va
   bien, `ChatResource.post` responde con `{ message, user }`.
5. `chat.js` pinta la respuesta y luego llama `/api/mensajes` de la web
   para persistir el par `(mensaje, respuesta)`. Ese segundo salto lo hace
   la web por el servidor contra la API, con el token de la sesión.

## Autorización

Autenticación ≠ autorización:

- Autenticación: "el token es válido y no está expirado".
- Autorización: "aunque el token sea válido, el usuario tiene permiso
  para este recurso concreto".

Dónde aparecen:

- `GET /api/mensajes`: si no es admin, la query se filtra automáticamente
  por su `user_id`. No hay forma de ver mensajes de otros.
- `GET/DELETE /api/mensajes/<id>`: check explícito
  `current.is_admin or mensaje.user_id == current.id`. Si no pasa, 403.
- `GET /api/users`: `roles_required("admin")` bloquea a todo el que no
  sea admin.
- `POST /api/chat`: solo requiere token válido. El chat no tiene recursos
  que dependan del usuario, así que no hay chequeo adicional.

## Logout

`/logout` hace `session.clear()` y redirige a `/`. El token JWT no se
invalida en el servidor (Praetorian no mantiene blacklist en esta
práctica): simplemente deja de estar en la sesión, así que el navegador
no lo volverá a enviar. Si alguien lo capturó antes de expirar, seguiría
valiendo hasta que caduque (`JWT_ACCESS_LIFESPAN = 2h`).
