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



## TP06

### Reglas de Negocio Agregadas

Para justificar las pruebas unitarias, se agrego:

- **Validación de Título vacío**
    - El endpoint `POST /api/todos` trima (`strip()`) el campo `title`
    - Si el resultado e suna cadena vacía, devuelve **400** con `detail = "title must not be empty"`
    - Esto es para evitar TODOs dificiles de identificar

- **Titulos únicos**
    - Antes de crear un TODO, se llama `store.list()` y se verifica que no exista otro registro con `title.lower()` igual.
    - Si ya existe, devuelve **400** con `detail = "title must be unique"`.
    - Esto es para mantener la lista de tareas consistente y no tener multiples filas con el mismo título

Ambas reglas se implementan en `backend/app/main.py` dentro del handler `create_todo`.

### Estrategia de pruebas unitarias – Backend

- **Framework**: `pytest` + `fastapi.testclient`.
- **Aislamiento de la base de datos**:
  - Se creó un `FakeStore` en `backend/tests/test_todos_routes.py`, que implementa los métodos usados por los endpoints (`list`, `add`).
  - Se usa `app.dependency_overrides[get_store]` para inyectar este fake en los tests, de modo que **no se usa la SQLite real**.
- **Casos cubiertos**:
  - `/healthz`: responde 200 con `{"status": "ok"}`.
  - `/api/todos` (GET): devuelve exactamente la lista que entrega el `FakeStore`.
  - `/api/todos` (POST):
    - caso feliz: crea un TODO nuevo y delega en `store.add()`,
    - error por título vacío,
    - error por título duplicado (case-insensitive).
  - `/admin/seed`:
    - 401 cuando el header `X-Seed-Token` no coincide con `settings.SEED_TOKEN`,
    - caso exitoso mockeando `seed_if_empty` con `monkeypatch` sobre `app.main.seed_if_empty`, para verificar que el endpoint:
      - valida el token,
      - llama a la función de seed,
      - devuelve un JSON con la info devuelta por la función fake.

### Estrategia de pruebas unitarias – Frontend

- **Framework**: Angular 18 + Karma + Jasmine.
- **Configuración**:
  - Se agregó `karma.conf.js`, `src/test.ts` y `tsconfig.spec.json` para definir el target `test`.
  - En `angular.json` se agregó `architect.test` con builder `@angular-devkit/build-angular:karma`.
- **Tests de servicio (`ApiService`) – `api.service.spec.ts`**:
  - Se usa `HttpClientTestingModule` y `HttpTestingController` para interceptar las requests HTTP.
  - Se fuerza `window.__env = { apiBase: 'http://fake-api/' }` para simular el `env.js` que se genera en el pipeline.
  - Casos probados:
    - `health()` hace `GET http://fake-api/healthz`.
    - `listTodos()` hace `GET http://fake-api/api/todos` y devuelve la lista esperada.
    - `addTodo(title)` hace `POST http://fake-api/api/todos` con body `{ title }`.

- **Tests de componente (`AppComponent`) – `app.component.spec.ts`**:
  - Se testea la **lógica de la clase**, no el template.
  - Se inyecta un `ApiServiceStub` con `health`, `listTodos` y `addTodo` mockeados (Jasmine spies).
  - Casos probados:
    - El constructor llama a `refresh()`, que a su vez llama a `health()` y `listTodos()` y carga el estado inicial de `todos`.
    - `add()`:
      - no llama al servicio si `newTitle` está vacío o son solo espacios,
      - aplica `trim()` al título antes de llamar al servicio,
      - agrega el TODO al array (`signal todos`),
      - resetea `newTitle` a cadena vacía,
      - deja `loading` en `false` al finalizar.

### Integración de tests en el pipeline CI/CD

- **Backend (job `backend`)**:
  - Se ejecuta:

    ```yaml
    - script: |
        set -e
        pytest --junitxml=TEST-backend.xml
      displayName: 'Run backend unit tests'
      workingDirectory: backend
    ```

  - Luego se publica el resultado JUnit:

    ```yaml
    - task: PublishTestResults@2
      displayName: 'Publish backend unit test results'
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: '**/TEST-*.xml'
        failTaskOnFailedTests: true
    ```

  - Si un test falla, el job falla y el stage `Build` no continúa.

- **Frontend (job `frontend`)**:
  - Se corre `npm test` en modo headless/CI:

    ```yaml
    - script: |
        set -e
        cd frontend
        npm test -- --watch=false --browsers=ChromeHeadless
      displayName: 'Run frontend unit tests'
    ```

  - Solo si los tests pasan se ejecuta `ng build` y se publica el artefacto `front.zip`.

- **Quality gate**:
  - Los stages `DeployQA` y `DeployPROD` dependen del stage `Build` y tienen `condition: succeeded()`.
  - Resultado: **no hay despliegue a QA ni a Producción si algún test unitario de backend o frontend falla**, alineado con los objetivos del TP06.
