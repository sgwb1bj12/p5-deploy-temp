# Práctica 5 — Microservicios, APIs RESTful y JWT

Aplicación basada en la práctica 4 reorganizada en microservicios.

## Estructura

```
p5/
├── docs/        capturas y documentación por ejercicio
│   ├── 1/
│   └── svaia/
├── infra/       MariaDB + phpMyAdmin (docker compose)
└── src/
    ├── 1/       Ejercicio 1: aplicación web + microservicio de datos
    └── svaia/   SVAIA: app unificada con JWT y SQLite (PythonAnywhere)
```

## Ejercicios

- **Ejercicio 1** — Microservicio de datos y usuarios. Ver
  [`src/1/README.md`](src/1/README.md) y
  [`docs/1/arquitectura.md`](docs/1/arquitectura.md).
- **SVAIA** — Aplicación unificada con JWT, SQLite y despliegue en
  PythonAnywhere. Ver [`src/svaia/README.md`](src/svaia/README.md).

## Entrega

- Rama de aula: `feature/p5-aula`
- Rama de entrega: `feature/p5-entrega`
- Tag de aula: `p5-aula`
- Tag de entrega: `p5-entrega`
