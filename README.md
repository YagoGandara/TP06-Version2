# TP05 - CI/CD (Angular + FastApi)

App mínima para establecer **CI/CD** con Azure DevOps, y desplegarlo en **Azure App Service** en entorno de **QA** y **Producción**

## Stack (Estructura) 
- **Frontend**: Angular 18 (SPA)
- **Backend**: FastAPI (Python 3.12)
- **DB**: SQLite por entorno (persiste en /home/data/app.db)
- **Infra**: Azure Web Apps (Linux, App Service Plan)
- **CI/CD**: Azure DevOps Pipelines (multi-stage con un solo artefacto en el Front)
- **Healthchecks**: `/`, `/healtz`, `/readyz`

---

## Acceso a los servicios (URLS)

**QA**
- Frontend (SPA): https://web-tp05-qa-gandara-f2byd8e5hkdzc7ac.brazilsouth-01.azurewebsites.net/ 
- Backend API: https://api-tp05-qa-gandara-gkafgvctgjhactc0.brazilsouth-01.azurewebsites.net/

**PROD**
- Frontend (SPA): https://web-tp05-prod-gandara-emhwhrahafezasdm.brazilsouth-01.azurewebsites.net/
- Backend API: https://api-tp05-prod-gandara-ckczhscna5dyeye2.brazilsouth-01.azurewebsites.net/

---

## Endpoints Útiles (API)

- `GET /` -> ping basico
- `GET /healtz` -> Estado de la app
- `GET /readyz` -> el pipeline o usa como health / gate
- `GET /api/todos` -> lista todos
- `POST /api/todos` -> crea (body : `{ "title": "texto" }`)

## Endpoints internos de mantenimiento o Seed
- `POST /admin/seed`
Header : `X-Seed-Token: <token>`
Ejecuta el seed si la tabla está vacía

- `GET /admin/debug`
Devuelve `db_url` y si existe el archivo de DB (para verificar la configuracion)

- `GET /admin/touch` 
Devuelve `{"count": n}` con el total de registros
---

## Local (Docker)

```bash
docker compose down -v
docker compose build
docker compose up 

```
- Front http://localhost:4200
- API http://localhost:8080

Para testear el backend con Docker
```bash
docker compose run --rm api-tests
```

## Local Puro 
* Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate 
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```
* Frontend
```bash
cd frontend
npm ci
npm start 
```
---
## Configuración por Entorno

# API - App Setting (QA | PROD)

| Nombre | Valor | Disclaimer |
|---:|:-------|:-------|

| ENV | qa/prod | etiqueta de entorno|
| API_PORT | 8080 | puerto de uvicorn |
| DB_URL | `sqlite:////home/data/app.db`| persistente en `/home/data` |
| CORS_ORIGIN | `<URL de cada Front>`| ejemplo: `https//web-...azuerwebsites.net` |
| SEED_TOKEN | `<Secreto>`| usado por `/admin/seed` |
| SEED_ON_START | `false`| ejecuta seed al boot si está vacío |

El container genera las tablas al iniciar `Base.metadata.create_all(bind=engine)`

---
## Front - Inyección de URL de API

El front se construye una sola vez y, en cada deploy, se superpone un archivo `assets/env.js` con:

```bash
window.__env = { apiBase: "<URL de la API del entorno>" };
```
El codigo de Angular toma `window.__env?.apiBase || environment.apiBaseUrl`, para que el mismo build funcione para QA y PROD

---

## CI(Build) - Azure DevOps

El pipeline `azure-pipelines.yml`:
- Front: `npm ci && ng build` -> publica `front/front-dist.zip`
- Back: instala dependencias y `pytest` -> publica `back/backend.zip`

Se dispara cada vez que haya un push a main

---

## CD (Release) - QA y PROD

# Build
1) **Frontend**
    - `npm ci && ng build --configuration=production`
    - Genera `dist/tp05-web/` y se publica como artefacto `front.zip`

2) **Backend**
    - `pip install -r requirements.txt`
    - Se empaqueta como `backend/` completo como `backend.zip`

#Release (Stages DeployQA y DeployPROD)
1) **DeployQA**
    - Despliega FRONT (`front.zip`) a WebbAppQa (zipDeploy)
    - Genera y despliega `env-qa.zip` para sobreescribir `assets/env.js`
    - Despliega API (`backend.zip`)
    - Seed DB(QA):
        ```bash
            curl -X POST "$API_QA/admin/seed" -H "X-Seed-Token: $(seedTokenQA)"
        ```

2) **DeployPROD**
    - Requiere aprobación manual del Environment PROD
    - Igual a QA, pero con `env-prod.zip` y `$(seedTokenPROD)`

Se dejaron smoke tests listos, pero no se implementaron porque se daban de baja los App Services

---

## Problemas y Troubleshootings

- **Front devuelve 404**: Se verifico que el ZIP publicado tenga el `index.html` en la raíz `wwwroot`. En Kudu/SSH debería verse las cosas ubicandose en el directorio `site/wwwroot`
- **`/api/todos` lanzaba 500**: en QA se corrigió asegurando que `DB_URL=sqlite:////home/data/app.db` y que la carpeta `/home/data` existieran (de no ser así, el código crea la ruta)
- **Seed no se corria**: Se verificó que los Token fueran los correctos, y fue solucionado cuando se logró corregir el problema 2 