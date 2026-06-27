# Servicio de Sanciones (servicio-sanciones)

## Descripción
Este microservicio regula la buena conducta de los usuarios al hacer uso de los ambientes de la universidad. Permite a los administradores aplicar y levantar penalizaciones (sanciones) a docentes o estudiantes por el mal uso de instalaciones (ej. no asistir a una reserva sin cancelar, causar daños). Los usuarios sancionados pierden privilegios en los demás microservicios (como reservar un laboratorio nuevo) mientras su sanción esté activa.

## Arquitectura
- **Frontend:** React (Panel "Gestión de Sanciones" y alertas informativas al usuario sancionado).
- **Backend:** Laravel (`servicio-sanciones`, controlador `SancionController` y utilidades de búsqueda en `UsuarioBusquedaController`).
- **Base de Datos:** MySQL (Tabla: `sancion`, dependencias a la tabla `usuario`).

---

## 1. Función: Verificación de Sanciones (Middleware de Negocio)

### Descripción
Este es el endpoint más consultado por los demás microservicios. Antes de que el `servicio-reserva` permita a un usuario agendar un espacio, se comunica con este servicio para comprobar si el usuario está habilitado o tiene un castigo pendiente.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor MicroservicioReserva
    participant SancionController
    participant SancionService
    participant Database

    MicroservicioReserva->>SancionController: GET /api/sanciones/estado?usuarioId=123
    
    SancionController->>SancionService: tieneSancionActiva(123)
    
    SancionService->>Database: SELECT COUNT(*) FROM sancion WHERE usuario = 123 AND estado = 'ACTIVA' AND fechaFin >= HOY
    
    alt Usuario Castigado
        Database-->>SancionService: Count > 0
        SancionService-->>SancionController: { sancionado: true }
        SancionController-->>MicroservicioReserva: HTTP 200 JSON
    else Usuario Limpio
        Database-->>SancionService: Count = 0
        SancionService-->>SancionController: { sancionado: false }
        SancionController-->>MicroservicioReserva: HTTP 200 JSON
    end
```

---

## 2. Función: Imponer y Levantar Sanción (Administrativo)

### Descripción
Un administrador puede buscar usuarios, imponerles una sanción definiendo el motivo y el rango de fechas (Inicio y Fin), o levantar prematuramente una sanción activa si el caso se resuelve por apelación o cumplimiento de servicio.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant UsuarioBusquedaController
    participant SancionController
    participant SancionService
    participant Database

    %% Buscar Usuario
    Admin->>Frontend: Escribe "Juan Perez"
    Frontend->>UsuarioBusquedaController: GET /api/usuarios/busqueda?query=Juan%20Perez
    UsuarioBusquedaController->>Database: Buscar en usuarios (LIKE %Juan Perez%)
    Database-->>UsuarioBusquedaController: Lista de IDs
    UsuarioBusquedaController-->>Frontend: Resultados
    
    %% Aplicar Sanción
    Admin->>Frontend: Sancionar a Juan por 1 semana (Motivo: Dañó microscopio)
    Frontend->>SancionController: POST /api/sanciones {usuarioId, fechaInicio, fechaFin, motivo}
    SancionController->>SancionService: registrarSancion()
    SancionService->>Database: INSERT INTO sancion
    Database-->>SancionService: Sanción Registrada
    SancionService-->>SancionController: Sancion
    SancionController-->>Frontend: HTTP 201 JSON
    
    %% Levantar Sanción
    Admin->>Frontend: Clic en "Perdonar Sanción"
    Frontend->>SancionController: PATCH /api/sanciones/{id}/levantar
    SancionController->>SancionService: levantarSancion(id)
    SancionService->>Database: UPDATE sancion SET estado = 'CUMPLIDA' WHERE id = ?
    Database-->>SancionService: OK
    SancionService-->>SancionController: Sanción modificada
    SancionController-->>Frontend: HTTP 200 JSON
```
