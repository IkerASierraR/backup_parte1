# Servicio Moodle (servicio-moodle)

## Descripción
Este microservicio actúa como un puente o gateway de integración entre la intranet universitaria y la plataforma virtual de aprendizaje (Moodle). Permite a los usuarios enlazar sus cuentas institucionales, usar Single Sign-On (SSO) y consultar directamente sus cursos matriculados, calificaciones y próximos eventos o tareas del aula virtual sin tener que salir de la aplicación de la universidad.

## Arquitectura
- **Frontend:** React (Sección "Aula Virtual" con flujos de autenticación OAuth/SSO).
- **Backend:** Laravel (`servicio-moodle`, controlador `MoodleController` y `MoodleService`).
- **Integración Externa:** Se comunica mediante API REST / Web Services con la instancia externa de Moodle.
- **Base de Datos:** MySQL (Almacena tokens de acceso en tabla asociada al usuario).

---

## 1. Función: Conexión de Cuenta y SSO (Single Sign-On)

### Descripción
Un usuario puede vincular su cuenta de dos formas: ingresando su usuario y contraseña de Moodle directamente (`conectar`) o iniciando un flujo seguro SSO (`iniciarSso` y `confirmarSso`), que evita manejar credenciales.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant MoodleController
    participant MoodleService
    participant ExternalMoodle
    participant Database

    %% Conexión Vía SSO
    Usuario->>Frontend: Clic en "Conectar con Moodle"
    Frontend->>MoodleController: GET /api/sso/iniciar?usuarioId=...
    
    MoodleController->>MoodleService: generarPassport()
    MoodleService-->>MoodleController: UUID passport
    MoodleController-->>Frontend: HTTP 200 {passport, launchUrl}
    
    Frontend->>Frontend: Redirige a Moodle (launchUrl)
    Usuario->>ExternalMoodle: Autoriza el acceso en Moodle
    ExternalMoodle->>Frontend: Callback Redirect (con Token)
    
    Frontend->>MoodleController: POST /api/sso/confirmar {passport, token, siteid...}
    MoodleController->>MoodleService: confirmarSso(...)
    MoodleService->>Database: Guarda Token de Acceso para el usuario
    Database-->>MoodleService: OK
    MoodleService-->>MoodleController: Éxito
    MoodleController-->>Frontend: HTTP 201 JSON
    
    %% Consultar Estado
    Frontend->>MoodleController: GET /api/estado?usuarioId=...
    MoodleController->>MoodleService: obtenerEstado()
    MoodleService->>Database: SELECT token_moodle FROM usuarios...
    Database-->>MoodleService: Token existente
    MoodleService-->>MoodleController: { conectado: true }
    MoodleController-->>Frontend: Renderiza Dashboard de Cursos
```

---

## 2. Función: Consultar Cursos, Tareas y Notas

### Descripción
Una vez vinculada la cuenta, el usuario puede ver la lista de cursos en los que está matriculado actualmente, así como consultar su libreta de notas (calificaciones) y próximos eventos del calendario (tareas que vencen pronto).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant MoodleController
    participant MoodleService
    participant Database
    participant ExternalMoodle

    %% Cursos
    Usuario->>Frontend: Va a "Mis Cursos"
    Frontend->>MoodleController: GET /api/cursos?usuarioId=...
    
    MoodleController->>MoodleService: obtenerCursos(usuarioId)
    MoodleService->>Database: Recupera Token
    MoodleService->>ExternalMoodle: Call WS core_enrol_get_users_courses
    ExternalMoodle-->>MoodleService: JSON Cursos
    MoodleService-->>MoodleController: Array de cursos adaptado
    MoodleController-->>Frontend: HTTP 200 JSON
    
    %% Calificaciones
    Usuario->>Frontend: Ver Notas de "Física"
    Frontend->>MoodleController: GET /api/cursos/{cursoId}/notas
    MoodleController->>MoodleService: obtenerNotas(cursoId)
    MoodleService->>ExternalMoodle: Call WS gradereport_user_get_grade_items
    ExternalMoodle-->>MoodleService: JSON Notas
    MoodleService-->>MoodleController: Array de calificaciones
    MoodleController-->>Frontend: HTTP 200 JSON
    
    %% Eventos / Tareas
    Usuario->>Frontend: Ver Tareas Pendientes
    Frontend->>MoodleController: GET /api/eventos?usuarioId=...
    MoodleController->>MoodleService: obtenerEventosProximos()
    MoodleService->>ExternalMoodle: Call WS core_calendar_get_action_events_by_timesort
    ExternalMoodle-->>MoodleService: JSON Eventos
    MoodleService-->>MoodleController: Array de Tareas/Eventos
    MoodleController-->>Frontend: HTTP 200 JSON
```
