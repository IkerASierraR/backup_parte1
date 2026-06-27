# Servicio de Buses Universitarios (servicio-burra)

## Descripción
> [!WARNING]
> **Código Duplicado Detectado:** Al analizar el código fuente de este microservicio (`servicio-burra`), se encontró que los controladores y rutas corresponden exactamente al módulo de **Psicología** (`PsicologiaController.php`). No existe lógica implementada para "Burras" (buses) en este directorio. A continuación se documenta el flujo real encontrado en el código.

Este microservicio (actualmente con lógica duplicada de Psicología) gestiona la lectura de profesionales psicólogos, visualización de sus bloques horarios disponibles, así como el registro y cancelación de citas por parte de un usuario.

## Arquitectura
- **Backend:** Laravel (`servicio-burra`, contiene `PsicologiaController` y delega a `PsicologiaService`).
- **Base de Datos:** MySQL (Lógica de inserción de citas, lectura de psicólogos).

---

## 1. Función: Listar Psicólogos

### Descripción
Devuelve la lista de profesionales en psicología registrados en el sistema.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant PsicologiaController
    participant PsicologiaService
    participant Database

    Usuario->>Frontend: Navega a la vista
    Frontend->>PsicologiaController: GET /api/psicologos
    
    PsicologiaController->>PsicologiaService: listarPsicologos()
    PsicologiaService->>Database: SELECT * FROM psicologos
    Database-->>PsicologiaService: Lista
    
    PsicologiaService-->>PsicologiaController: Array
    PsicologiaController-->>Frontend: HTTP 200 JSON
```

---

## 2. Función: Consultar Bloques Disponibles

### Descripción
Dado un `psicologoId` y una `fecha`, devuelve los bloques de horario disponibles para reservar una cita.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant PsicologiaController
    participant PsicologiaService
    participant Database

    Usuario->>Frontend: Selecciona Fecha
    Frontend->>PsicologiaController: GET /api/psicologos/{psicologoId}/bloques-disponibles?fecha=YYYY-MM-DD
    
    PsicologiaController->>PsicologiaController: Valida fecha != null
    
    PsicologiaController->>PsicologiaService: listarBloquesDisponibles(psicologoId, fecha)
    PsicologiaService->>Database: SELECT bloques libres...
    Database-->>PsicologiaService: Lista de Bloques
    
    PsicologiaService-->>PsicologiaController: Data
    PsicologiaController-->>Frontend: HTTP 200 JSON
```

---

## 3. Función: Registrar Cita

### Descripción
Recibe un payload JSON para registrar una nueva cita en el horario seleccionado. Puede arrojar conflicto (HTTP 409) si el horario ya fue tomado concurrentemente, o HTTP 400 si faltan datos.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant PsicologiaController
    participant PsicologiaService
    participant Database

    Usuario->>Frontend: Clic en Confirmar Cita
    Frontend->>PsicologiaController: POST /api/citas {datos de cita}
    
    PsicologiaController->>PsicologiaService: registrarCita(request->all())
    
    alt Datos Inválidos
        PsicologiaService-->>PsicologiaController: throw InvalidArgumentException
        PsicologiaController-->>Frontend: HTTP 400 Bad Request
    else Horario Ocupado
        PsicologiaService-->>PsicologiaController: throw LogicException
        PsicologiaController-->>Frontend: HTTP 409 Conflict
    else Éxito
        PsicologiaService->>Database: INSERT INTO citas ...
        Database-->>PsicologiaService: Cita registrada
        PsicologiaService-->>PsicologiaController: Cita
        PsicologiaController-->>Frontend: HTTP 201 Created
    end
```

---

## 4. Función: Cancelar Cita

### Descripción
Cancela una cita agendada por el usuario, liberando el bloque. Requiere el `id` de la cita y el `usuarioId` en los parámetros.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant PsicologiaController
    participant PsicologiaService
    participant Database

    Usuario->>Frontend: Clic en "Cancelar Cita"
    Frontend->>PsicologiaController: DELETE /api/citas/{id}?usuarioId=...
    
    PsicologiaController->>PsicologiaService: cancelarCita(id, usuarioId)
    
    PsicologiaService->>Database: SELECT * FROM citas WHERE id=? AND usuarioId=?
    
    alt Cita no existe
        PsicologiaService-->>PsicologiaController: throw InvalidArgumentException
        PsicologiaController-->>Frontend: HTTP 404 Not Found
    else Reglas de negocio incumplidas (ej. tiempo)
        PsicologiaService-->>PsicologiaController: throw LogicException
        PsicologiaController-->>Frontend: HTTP 409 Conflict
    else Éxito
        PsicologiaService->>Database: UPDATE citas SET estado='Cancelado'...
        Database-->>PsicologiaService: OK
        PsicologiaService-->>PsicologiaController: Cita actualizada
        PsicologiaController-->>Frontend: HTTP 200 JSON
    end
```
