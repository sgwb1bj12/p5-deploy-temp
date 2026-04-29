import os

import requests


API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:5202")
TIMEOUT = 5


def autenticar(username, password):
    resp = requests.post(
        f"{API_BASE_URL}/api/auth/login",
        json={"username": username, "password": password},
        timeout=TIMEOUT,
    )
    if resp.status_code != 200:
        return None
    return resp.json()


def listar_mensajes(token, owner_id=None):
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if owner_id is not None:
        params["owner_id"] = owner_id
    resp = requests.get(
        f"{API_BASE_URL}/api/mensajes",
        headers=headers,
        params=params,
        timeout=TIMEOUT,
    )
    if resp.status_code != 200:
        return []
    return resp.json()


def crear_mensaje(token, contenido, respuesta):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(
        f"{API_BASE_URL}/api/mensajes",
        headers=headers,
        json={"contenido": contenido, "respuesta": respuesta},
        timeout=TIMEOUT,
    )
    if resp.status_code != 201:
        return None
    return resp.json()


def eliminar_mensaje(token, mensaje_id):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(
        f"{API_BASE_URL}/api/mensajes/{mensaje_id}",
        headers=headers,
        timeout=TIMEOUT,
    )
    return resp.status_code == 200


def listar_usuarios(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{API_BASE_URL}/api/users",
        headers=headers,
        timeout=TIMEOUT,
    )
    if resp.status_code != 200:
        return []
    return resp.json()
