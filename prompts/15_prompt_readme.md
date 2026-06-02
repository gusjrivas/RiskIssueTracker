# Prompt 15 — README del proyecto

## Contexto
Documentación completa del proyecto para que cualquier persona pueda levantarlo y entender la arquitectura.

## Prompt
```
ahora revisa todo el proyecto y arma un readme claro y detallado para que cualquier 
persona pueda levantar el proyecto. los autores del proyecto son Gustavo Julián Rivas 
y Rodolfo Di Chiazza
```

## Contenido del README generado

### Secciones
1. **Descripción y autores** — propósito de la app y créditos
2. **Stack tecnológico** — tabla con backend, frontend, DB, auth, infra, testing
3. **Arquitectura** — diagrama ASCII de Docker Compose + diagrama de capas del backend + flujo de estados
4. **Requisitos previos** — solo Docker Desktop (no requiere Python ni Node locales)
5. **Levantar el proyecto** — 4 pasos: clonar → .env → `docker compose up --build` → verificar
6. **Primer usuario admin** — 3 comandos exactos para crear y aprobar el primer admin
7. **Variables de entorno** — tabla completa con cuáles son requeridas y cuáles opcionales
8. **Estructura del proyecto** — árbol de carpetas comentado
9. **API Reference** — tabla con 25 endpoints: método, ruta, descripción y nivel de auth
10. **Cálculo de severidad** — tablas de pesos, zonas y matriz con ejemplo numérico
11. **Testing** — comandos para pytest y vitest con opciones de cobertura
12. **Comandos útiles** — Docker, psql, Alembic listos para copiar/pegar
13. **Licencia** — con autores y año

## Archivo generado
`README.md` en la raíz del proyecto
