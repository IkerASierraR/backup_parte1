# Servicio de Incidencias (servicio-incidencia)

## Descripción
Este microservicio está destinado al reporte de problemas, daños o anomalías encontradas en los espacios físicos después de una reserva (por ejemplo, proyector dañado, sillas rotas, limpieza deficiente). Permite a los usuarios registrar la incidencia y a los administradores gestionar su seguimiento.

## Arquitectura
- **Frontend:** React (Sección de "Mis Reservas" para reportar problemas, y "Panel de Incidencias" para administradores).
- **Backend:** Laravel (`servicio-incidencia`, controlador `IncidenciaController`).
- **Base de Datos:** MySQL (Tablas esperadas: `incidencias`, relacionándose indirectamente con `reservas` y `usuarios`).

---

## 1. Función: Reportar una Incidencia

### Descripción
Permite a un usuario (estudiante o docente) que ha hecho uso de una reserva, reportar un problema ocurrido durante la misma.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant IncidenciaController
    participant IncidenciaService
    participant Database

    Usuario->>Frontend: Escribe detalle de incidencia y envía
    Frontend->>IncidenciaController: POST /api/incidencias {reservaId, detalle...}
    
    IncidenciaController->>IncidenciaController: Valida Request
    IncidenciaController->>IncidenciaService: registrarIncidencia(datos)
    
    IncidenciaService->>Database: Verifica existencia de reserva
    
    alt Reserva no encontrada
        Database-->>IncidenciaService: null
        IncidenciaService-->>IncidenciaController: throw ModelNotFoundException
        IncidenciaController-->>Frontend: HTTP 404 Not Found
    else Regla de negocio no cumplida
        IncidenciaService-->>IncidenciaController: throw LogicException (Ej. ya se reportó)
        IncidenciaController-->>Frontend: HTTP 409 Conflict
    else Válido
        IncidenciaService->>Database: INSERT INTO incidencias ...
        Database-->>IncidenciaService: OK
        IncidenciaService-->>IncidenciaController: Incidencia
        IncidenciaController-->>Frontend: HTTP 201 Created
    end
```

---

## 2. Función: Gestión de Incidencias (Admin)

### Descripción
Lista todas las incidencias reportadas en el sistema, permitiendo filtrar por facultad, escuela, espacio o mediante una búsqueda de texto.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant IncidenciaController
    participant IncidenciaService
    participant Database

    Admin->>Frontend: Abre "Panel de Incidencias"
    Frontend->>IncidenciaController: GET /api/incidencias?facultadId=...&search=...
    
    IncidenciaController->>IncidenciaService: listarParaGestion(filtros...)
    IncidenciaService->>Database: SELECT * FROM incidencias WHERE (filtros dinámicos)
    Database-->>IncidenciaService: Lista
    
    IncidenciaService-->>IncidenciaController: Array
    IncidenciaController-->>Frontend: HTTP 200 JSON
    Frontend-->>Admin: Renderiza tabla de problemas a resolver
```

---

## 3. Función: Consultar Historial y Disponibilidad de Reserva

### Descripción
El sistema provee endpoints auxiliares para saber si una reserva específica permite aún reportar incidencias (`verificarDisponibilidad`), ver el historial de problemas de una reserva y listar las reservas pasadas de un usuario para que pueda reportar sobre ellas.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant IncidenciaController
    participant IncidenciaService
    participant Database

    %% Buscar Reservas del Usuario
    Usuario->>Frontend: Va a "Mis Reservas"
    Frontend->>IncidenciaController: GET /api/incidencias/usuario/{usuarioId}/reservas
    IncidenciaController->>IncidenciaService: listarReservasParaUsuario(usuarioId)
    IncidenciaService->>Database: SELECT * FROM reservas WHERE usuarioId = ?
    Database-->>IncidenciaService: Reservas
    IncidenciaService-->>IncidenciaController: Array
    IncidenciaController-->>Frontend: HTTP 200 JSON
    
    %% Verificar si puede reportar
    Frontend->>IncidenciaController: GET /api/incidencias/reserva/{id}/disponibilidad
    IncidenciaController->>IncidenciaService: verificarDisponibilidad(id)
    IncidenciaService->>Database: COUNT incidencias para reserva
    Database-->>IncidenciaService: Conteo y estado
    IncidenciaService-->>IncidenciaController: { puedeReportar: true/false }
    IncidenciaController-->>Frontend: HTTP 200 JSON
    Frontend-->>Usuario: Habilita/Deshabilita botón "Reportar Problema"
```
