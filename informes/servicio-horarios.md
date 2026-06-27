# Servicio de Horarios (servicio-horarios)

## Descripción
Este microservicio administra la disponibilidad horaria de los diferentes espacios físicos de la universidad. Define en qué bloques horarios (ej. 08:00 - 10:00) y qué días de la semana un espacio está disponible u ocupado. Es consumido fundamentalmente por el sistema de reservas para saber cuándo se puede agendar un ambiente.

## Arquitectura
- **Frontend:** React (Calendarios y vistas de disponibilidad de espacios).
- **Backend:** Laravel (`servicio-horarios`, controlador `HorarioController`).
- **Base de Datos:** MySQL (Tablas: `horarios`, con llaves foráneas a `espacios` y `bloques`).

---

## 1. Función: Consultar Disponibilidad de un Espacio

### Descripción
Recupera el horario de un espacio particular, ya sea en un formato lineal (lista) o estructurado en formato semanal (matriz Día x Bloque).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant HorarioController
    participant HorarioService
    participant Database

    Usuario->>Frontend: Selecciona un Laboratorio para ver su calendario
    Frontend->>HorarioController: GET /api/horarios/espacio/{espacioId}/semanal
    
    HorarioController->>HorarioService: obtenerHorarioSemanalPorEspacio(espacioId)
    
    HorarioService->>Database: SELECT * FROM horarios WHERE espacioId = ?
    Database-->>HorarioService: Lista de Horarios
    
    HorarioService->>HorarioService: Estructura datos por día (Lunes, Martes...) y bloque
    
    HorarioService-->>HorarioController: Array estructurado
    HorarioController-->>Frontend: HTTP 200 JSON
    Frontend-->>Usuario: Renderiza el calendario semanal
```

---

## 2. Función: Buscar Espacios por Disponibilidad / Día

### Descripción
Permite listar todos los horarios que actualmente constan como "disponibles" (o bien ocupados), y también permite buscar qué hay programado en un día de la semana específico.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Sistema
    participant Frontend
    participant HorarioController
    participant HorarioService
    participant Database

    %% Buscar Disponibles
    Sistema->>Frontend: Filtrar solo espacios libres
    Frontend->>HorarioController: GET /api/horarios/disponibles
    HorarioController->>HorarioService: listarPorOcupacion(false)
    HorarioService->>Database: SELECT * FROM horarios WHERE ocupado = 0
    Database-->>HorarioService: Resultados
    HorarioService-->>HorarioController: Array
    HorarioController-->>Frontend: HTTP 200 JSON
    
    %% Buscar por Día
    Sistema->>Frontend: Filtrar por "Lunes"
    Frontend->>HorarioController: GET /api/horarios/dia/Lunes
    HorarioController->>HorarioService: listarPorDia('Lunes')
    HorarioService->>Database: SELECT * FROM horarios WHERE diaSemana = 'Lunes'
    Database-->>HorarioService: Resultados
    HorarioService-->>HorarioController: Array
    HorarioController-->>Frontend: HTTP 200 JSON
```

---

## 3. Función: CRUD y Cambio de Ocupación

### Descripción
Gestión administrativa de los horarios. Permite crear nuevos registros de disponibilidad y cambiar ágilmente el estado de ocupación de un horario específico (útil cuando se aprueba una reserva y ese bloque pasa a estar ocupado).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant HorarioController
    participant HorarioService
    participant Database

    %% Creación
    Admin->>Frontend: Asigna un bloque horario a un espacio
    Frontend->>HorarioController: POST /api/horarios {espacioId, bloqueId, diaSemana, ocupado}
    
    HorarioController->>HorarioController: Valida request
    HorarioController->>HorarioService: crearHorario(datos)
    
    HorarioService->>Database: Validar si ya existe ese cruce (espacio/bloque/día)
    alt Cruce detectado
        HorarioService-->>HorarioController: throw InvalidArgumentException
        HorarioController-->>Frontend: HTTP 400 Bad Request
    else No hay cruce
        HorarioService->>Database: INSERT INTO horarios ...
        Database-->>HorarioService: OK
        HorarioService-->>HorarioController: Horario
        HorarioController-->>Frontend: HTTP 201 JSON
    end
    
    %% Actualizar Ocupación
    Admin->>Frontend: Marca el bloque como "Ocupado"
    Frontend->>HorarioController: PATCH /api/horarios/{id}/ocupacion {ocupado: true}
    
    HorarioController->>HorarioService: actualizarOcupacion(id, true)
    HorarioService->>Database: UPDATE horarios SET ocupado = 1 WHERE id = ?
    Database-->>HorarioService: OK
    
    HorarioService-->>HorarioController: Horario Actualizado
    HorarioController-->>Frontend: HTTP 200 JSON
```
