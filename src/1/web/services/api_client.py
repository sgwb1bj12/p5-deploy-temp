import os

import requests


API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:5101")
TIMEOUT = 5


def _url(path):
    return f"{API_BASE_URL}{path}"


def autenticar(username, password):
    r = requests.post(
        _url("/api/auth"),
        json={"username": username, "password": password},
        timeout=TIMEOUT,
    )
    if r.status_code == 200:
        return r.json()
    return None


def obtener_usuario(user_id):
    r = requests.get(_url(f"/api/users/{user_id}"), timeout=TIMEOUT)
    if r.status_code == 200:
        return r.json()
    return None


def listar_tareas(owner_id=None):
    params = {}
    if owner_id is not None:
        params["owner_id"] = owner_id
    r = requests.get(_url("/api/tareas"), params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def crear_tarea(title, owner_id):
    r = requests.post(
        _url("/api/tareas"),
        json={"title": title, "owner_id": owner_id},
        timeout=TIMEOUT,
    )
    return r.status_code, r.json()


def actualizar_tarea(tarea_id, datos):
    r = requests.patch(_url(f"/api/tareas/{tarea_id}"), json=datos, timeout=TIMEOUT)
    return r.status_code, r.json()


def eliminar_tarea(tarea_id):
    r = requests.delete(_url(f"/api/tareas/{tarea_id}"), timeout=TIMEOUT)
    return r.status_code, r.json() if r.content else {}


def obtener_tarea(tarea_id):
    r = requests.get(_url(f"/api/tareas/{tarea_id}"), timeout=TIMEOUT)
    if r.status_code == 200:
        return r.json()
    return None
