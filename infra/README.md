# Infraestructura MariaDB + phpMyAdmin

Infraestructura compartida por los ejercicios de la práctica 5.

## Servicios

- `mariadb`: servidor MariaDB 11 en el puerto `3306`.
- `phpmyadmin`: interfaz de administración web en el puerto `8080`.

## Bases de datos creadas automáticamente

- `p5_ej1_tareas`

## Arranque

Desde esta carpeta:

```bash
docker compose --env-file .env -f docker-compose.yml up -d
```

## Parada

```bash
docker compose --env-file .env -f docker-compose.yml down
```
