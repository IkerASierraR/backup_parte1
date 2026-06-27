# Servicio de Psicología (servicio-psicologia)

## Descripción
Este microservicio gestiona las citas y atención del área de Bienestar Universitario, específicamente para el soporte psicológico de los estudiantes. Comparte gran parte de la estructura y lógica con el servicio del policlínico, pero se maneja de forma independiente para asegurar la privacidad y la segregación del staff (psicólogos vs médicos generales).

## Arquitectura
- **Frontend:** React (Módulo "Bienestar Estudiantil").
- **Backend:** Laravel (`servicio-psicologia`, controlador `PsicologiaController`).
- **Base de Datos:** MySQL (Tablas esperadas: `psicologo`, `cita_psicologia`).

---

## 1. Función: Reserva de Cita Psicológica (Estudiante)

### Descripción
El estudiante selecciona a un psicólogo (o se le asigna uno), visualiza sus horarios libres (bloques) para un día particular y agenda la cita, enviando opcionalmente un motivo.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Estudiante
    participant Frontend
    participant PsicologiaController
    participant PsicologiaService
    participant Database

    Estudiante->>Frontend: Selecciona Psicólogo y Fecha
    Frontend->>PsicologiaController: GET /api/psicologos/{id}/bloques-disponibles?fecha=YYYY-MM-DD
    
    PsicologiaController->>PsicologiaService: listarBloquesDisponibles(id, fecha)
    PsicologiaService->>Database: Filtra bloques vs citas agendadas
    Database-->>PsicologiaService: Horarios disponibles
    PsicologiaService-->>PsicologiaController: Array
    PsicologiaController-->>Frontend: HTTP 200 JSON
    
    Estudiante->>Frontend: Selecciona las 14:00 hrs y guarda
    Frontend->>PsicologiaController: POST /api/citas {psicologoId, bloqueId, fecha...}
    
    PsicologiaController->>PsicologiaService: registrarCita(datos)
    PsicologiaService->>Database: Valida disponibilidad concurrente
    
    alt Bloque ya ocupado
        Database-->>PsicologiaService: Error de conflicto
        PsicologiaService-->>PsicologiaController: throw LogicException
        PsicologiaController-->>Frontend: HTTP 409 Conflict
    else Válido
        PsicologiaService->>Database: INSERT INTO cita_psicologia
        Database-->>PsicologiaService: Creado
        PsicologiaService-->>PsicologiaController: Cita
        PsicologiaController-->>Frontend: HTTP 201 Created
    end
```

---

## 2. Función: Gestión de Citas (Psicólogo / Admin)

### Descripción
El psicólogo o personal administrativo puede listar las citas agendadas para el día y actualizar su estado (por ejemplo, a "Atendido", "Falta").

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Psicologo
    participant Frontend
    participant PsicologiaController
    participant PsicologiaService
    participant Database

    %% Ver Citas
    Psicologo->>Frontend: Carga agenda del día
    Frontend->>PsicologiaController: GET /api/admin/citas?psicologoId=...&fecha=...
    PsicologiaController->>PsicologiaService: listarCitasAdmin(filtros)
    PsicologiaService->>Database: SELECT * FROM cita_psicologia WHERE ...
    Database-->>PsicologiaService: Lista
    PsicologiaService-->>PsicologiaController: Array
    PsicologiaController-->>Frontend: HTTP 200 JSON
    
    %% Actualizar Estado
    Psicologo->>Frontend: Finaliza sesión (Marcar Atendido)
    Frontend->>PsicologiaController: PATCH /api/admin/citas/{id}/estado {estado: 'atendido'}
    PsicologiaController->>PsicologiaService: cambiarEstadoCita(id, 'atendido')
    PsicologiaService->>Database: UPDATE cita_psicologia SET estado = 'atendido' WHERE id = ?
    Database-->>PsicologiaService: OK
    PsicologiaService-->>PsicologiaController: Cita actualizada
    PsicologiaController-->>Frontend: HTTP 200 JSON
```

---

## 3. Función: Catálogo de Psicólogos (CRUD)

### Descripción
Permite a los administradores de Bienestar Universitario registrar a los psicólogos que atienden a los estudiantes y darles de baja cuando dejen de laborar.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant PsicologiaController
    participant PsicologiaService
    participant Database

    Admin->>Frontend: Añadir nuevo psicólogo
    Frontend->>PsicologiaController: POST /api/admin/psicologos {nombre, especialidad...}
    
    PsicologiaController->>PsicologiaService: crearPsicologo(datos)
    PsicologiaService->>Database: INSERT INTO psicologo
    Database-->>PsicologiaService: Creado
    PsicologiaService-->>PsicologiaController: OK
    PsicologiaController-->>Frontend: HTTP 201 JSON
```
