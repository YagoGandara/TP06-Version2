## Estrategia General

- **Un solo artefacto de Frontend**: el build de Angular se ejecuta una vez, y la **diferenciacion por entorno** se hace en deploy, superponiendo `assets/env.js` con la URL de la API correspondiente. Asi nos aseguramos que lo probado en QA sea idéntico a lo que se envía a PROD
- **Backend empaquetado una vez por commit**: Se publica `backend.zip` y se reutiliza en QA y PROD

---

## Base de Datos
- Se eligió una SQLite persistida en `/home/data/app.db` dentro de cada Web App para evitar costos adicionales que pudieran sumarse en Azure
- Cada entorno tiene su archivo DB **independiente** (es aislado por host)
- El ORM crea las tablas al iniciar, y el seed es opcional, expuesto por un endpoint protegido en `SEED_TOKEN`

---

## Configuración del Entorno
- **Variables de App Service**(controlan el comportamiento sin recompilar)
    1) ENV
    2) DB_URL
    3) CORS_ORIGIN
    4) SEED_TOKEN
    5) SEED_ON_START
 
- Para Front, `window.__env.apiBase` permite cambiar la API consumida sin hacer rebuild

---

## Pipeline
- **Build stage**
    1) Front: `ng build` (prod) -> publica `front.zip`
    2) Back: instala dependencias -> publica `backend.zip`

- **Deploy QA**
    1) Despliega `front.zip`
    2) Inyecta `env.js` con la API de QA
    3) Despliega `backend.zip`
    4) Ejecuta seed con token
    6) Smoke Test (si los habilito)

- **Deploy PROD**
    1) Rollout identico a QA
    2) Aprobación manual en Environment
    3) Seed de PROD con token propio

---
## CORS y seguridad del Seed

- `CORS_ORIGINS` reestringen el origen permitido del SPA por entorno
- `/admin/seed` requiere un heade `X-Seed-Token` y no hace nada si ya existen filas (no se expone en la interfaz del Front)
