# Servicio de Policlínico (servicio-policlinico)

## Descripción
Este microservicio gestiona la atención primaria de salud dentro del campus (Policlínico Universitario). Permite a los administradores gestionar los tipos de atención (medicina general, odontología, triaje), registrar a los médicos especialistas y controlar los horarios. Por el lado del paciente, permite consultar horarios disponibles y agendar o cancelar citas médicas.

## Arquitectura
- **Frontend:** React (Portal del Paciente para agendar citas y Portal Administrativo para gestión de médicos y estados de citas).
- **Backend:** Laravel (`servicio-policlinico`, controlador `PoliclinicoController`).
- **Base de Datos:** MySQL (Tablas: `policlinico_tipos_atencion`, `policlinico_medicos`, `policlinico_citas`).

---

## 1. Función: Reserva de Cita Médica (Paciente)

### Descripción
El paciente busca una especialidad (tipo de atención), elige un médico, consulta su horario disponible y reserva un bloque. Si el bloque se ocupó concurrentemente, el sistema rechaza la operación.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Paciente
    participant Frontend
    participant PoliclinicoController
    participant PoliclinicoService
    participant Database

    Paciente->>Frontend: Selecciona "Odontología" y elige Médico
    Frontend->>PoliclinicoController: GET /api/medicos/{id}/bloques-disponibles?fecha=YYYY-MM-DD
    
    PoliclinicoController->>PoliclinicoService: listarBloquesDisponibles(medicoId, fecha)
    PoliclinicoService->>Database: SELECT bloques libres vs citas asignadas
    Database-->>PoliclinicoService: Horarios
    PoliclinicoService-->>PoliclinicoController: Array
    PoliclinicoController-->>Frontend: HTTP 200 JSON
    
    Paciente->>Frontend: Selecciona las 10:00 AM y confirma
    Frontend->>PoliclinicoController: POST /api/citas {medicoId, bloqueId, fecha...}
    
    PoliclinicoController->>PoliclinicoService: registrarCita(datos)
    PoliclinicoService->>Database: Inicia Transacción -> Bloquea Registro
    
    alt Horario ya tomado
        Database-->>PoliclinicoService: Conflicto
        PoliclinicoService-->>PoliclinicoController: throw LogicException
        PoliclinicoController-->>Frontend: HTTP 409 Conflict
    else Horario libre
        PoliclinicoService->>Database: INSERT INTO policlinico_citas
        Database-->>PoliclinicoService: OK
        PoliclinicoService-->>PoliclinicoController: Cita
        PoliclinicoController-->>Frontend: HTTP 201 Created
    end
```

---

## 2. Función: Cancelar Cita (Paciente)

### Descripción
Un paciente puede cancelar su cita antes de la fecha programada, liberando así el bloque horario para otro paciente.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Paciente
    participant Frontend
    participant PoliclinicoController
    participant PoliclinicoService
    participant Database

    Paciente->>Frontend: Clic en "Cancelar Cita"
    Frontend->>PoliclinicoController: DELETE /api/citas/{id}?usuarioId=...
    
    PoliclinicoController->>PoliclinicoService: cancelarCita(id, usuarioId)
    PoliclinicoService->>Database: SELECT * FROM policlinico_citas WHERE id=? AND usuarioId=?
    
    alt Cita no encontrada o pertenece a otro
        Database-->>PoliclinicoService: null
        PoliclinicoService-->>PoliclinicoController: throw InvalidArgumentException
        PoliclinicoController-->>Frontend: HTTP 404 Not Found
    else Regla de negocio (Ej. muy tarde para cancelar)
        PoliclinicoService-->>PoliclinicoController: throw LogicException
        PoliclinicoController-->>Frontend: HTTP 409 Conflict
    else Cancelación Exitosa
        PoliclinicoService->>Database: UPDATE policlinico_citas SET estado = 'cancelado'
        Database-->>PoliclinicoService: OK
        PoliclinicoService-->>PoliclinicoController: Cita Actualizada
        PoliclinicoController-->>Frontend: HTTP 200 JSON
    end
```

---

## 3. Función: Gestión de Citas y Recepción (Administrativo)

### Descripción
El personal del policlínico visualiza todas las citas del día, filtra por médico o estado y actualiza el estado de la cita conforme el paciente avanza (Atendido, No Asistió).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Recepcionista
    participant Frontend
    participant PoliclinicoController
    participant PoliclinicoService
    participant Database

    %% Listar Citas del Día
    Recepcionista->>Frontend: Ve citas de "Medicina General" para "Hoy"
    Frontend->>PoliclinicoController: GET /api/admin/citas?fecha=...&tipoAtencionId=...
    PoliclinicoController->>PoliclinicoService: listarCitasAdmin(filtros)
    PoliclinicoService->>Database: SELECT * FROM policlinico_citas (filtros)
    Database-->>PoliclinicoService: Resultados
    PoliclinicoService-->>PoliclinicoController: Array
    PoliclinicoController-->>Frontend: HTTP 200 JSON
    
    %% Marcar como Atendido
    Recepcionista->>Frontend: Cambia estado de Juan Pérez a "Atendido"
    Frontend->>PoliclinicoController: PATCH /api/admin/citas/{id}/estado {estado: 'atendido'}
    PoliclinicoController->>PoliclinicoService: cambiarEstadoCita(id, 'atendido')
    PoliclinicoService->>Database: UPDATE policlinico_citas SET estado = 'atendido' WHERE id = ?
    Database-->>PoliclinicoService: OK
    PoliclinicoService-->>PoliclinicoController: Cita
    PoliclinicoController-->>Frontend: HTTP 200 JSON
```

---

## 4. Función: Administración del Catálogo (Especialidades y Médicos)

### Descripción
Mantenimiento CRUD para crear nuevos tipos de atención (triaje, enfermería, etc.) y registrar nuevos profesionales de la salud.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant PoliclinicoController
    participant PoliclinicoService
    participant Database

    %% Crear Especialidad
    Admin->>Frontend: Añade Especialidad "Psicología Clínica"
    Frontend->>PoliclinicoController: POST /api/admin/tipos-atencion {nombre...}
    PoliclinicoController->>PoliclinicoService: crearTipoAtencion(datos)
    PoliclinicoService->>Database: INSERT INTO policlinico_tipos_atencion
    Database-->>PoliclinicoService: Creado
    PoliclinicoService-->>PoliclinicoController: OK
    PoliclinicoController-->>Frontend: HTTP 201 JSON
    
    %% Registrar Médico
    Admin->>Frontend: Añade al Dr. Smith a "Psicología Clínica"
    Frontend->>PoliclinicoController: POST /api/admin/medicos {nombre, cmp, tipoAtencionId...}
    PoliclinicoController->>PoliclinicoService: crearMedico(datos)
    PoliclinicoService->>Database: INSERT INTO policlinico_medicos
    Database-->>PoliclinicoService: Creado
    PoliclinicoService-->>PoliclinicoController: OK
    PoliclinicoController-->>Frontend: HTTP 201 JSON
```
