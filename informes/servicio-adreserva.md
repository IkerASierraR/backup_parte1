# Servicio de Administración de Reservas (servicio-adreserva)

## Descripción
Este microservicio está diseñado para que los usuarios con rol de Administrador o Supervisor puedan listar, filtrar y gestionar (Aprobar/Rechazar) las reservas de espacios (aulas, laboratorios, canchas, etc.) realizadas por estudiantes o docentes.

## Arquitectura
- **Frontend:** React (Componentes en `GestionAdmin/GestionReservas`, Llamadas HTTP vía Axios o Fetch).
- **Backend:** PHP puro (Mini-framework propio con `App\Core\Router`), puerto de servicio.
- **Base de Datos:** MySQL (Tablas: `reserva`, `reserva_gestion`, `facultad`, `escuela`, `espacio`, `administrativo`).

---

## 1. Función: Listar Reservas

### Descripción
Obtiene un listado paginado o filtrado de todas las reservas y un resumen estadístico (Pendiente, Aprobada, Rechazada, Cancelada). Si el usuario es un "Supervisor", automáticamente se filtran los resultados a la facultad y escuela a la que pertenece.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant AdminReservaController
    participant AdminReservaService
    participant AdministrativoRepository
    participant ReservaRepository
    participant Database

    Admin->>Frontend: Accede a "Gestión de Reservas"
    Frontend->>AdminReservaController: GET /api/admin/reservas?estado=...&facultadId=...
    
    AdminReservaController->>AdminReservaService: obtenerReservas(filter)
    
    opt Es Supervisor
        AdminReservaService->>AdministrativoRepository: findByUsuarioId(usuarioId)
        AdministrativoRepository->>Database: SELECT escuelaId FROM administrativo
        Database-->>AdministrativoRepository: escuelaId
        AdministrativoRepository-->>AdminReservaService: Asignación (Facultad/Escuela)
    end
    
    AdminReservaService->>ReservaRepository: buscarReservasParaAdmin(filtros)
    ReservaRepository->>Database: SELECT * FROM reserva WHERE ...
    Database-->>ReservaRepository: Lista de reservas
    
    AdminReservaService->>ReservaRepository: obtenerResumenEstados(filtros)
    ReservaRepository->>Database: SELECT estado, COUNT(*) FROM reserva GROUP BY estado
    Database-->>ReservaRepository: Cantidades por estado
    
    AdminReservaService->>AdminReservaService: construirResumen()
    AdminReservaService-->>AdminReservaController: AdminReservaListResponse
    
    AdminReservaController-->>Frontend: HTTP 200 JSON {reservas, resumen}
    Frontend-->>Admin: Renderiza tabla y tarjetas resumen
```

---

## 2. Función: Obtener Filtros

### Descripción
Devuelve las opciones disponibles para poblar los selects (comboboxes) en la interfaz de usuario, como los tipos de espacio, facultades y escuelas. Si el usuario es "Supervisor", solo devuelve su propia facultad y escuela.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant AdminReservaController
    participant AdminReservaService
    participant EspacioRepository
    participant FacultadRepository
    participant EscuelaRepository
    participant Database

    Frontend->>AdminReservaController: GET /api/admin/reservas/filtros?rol=...&usuarioId=...
    
    AdminReservaController->>AdminReservaService: obtenerFiltros(usuarioId, rol)
    
    AdminReservaService->>EspacioRepository: obtenerTiposDeEspacio()
    EspacioRepository->>Database: SELECT DISTINCT tipo FROM espacio
    Database-->>EspacioRepository: Lista de Tipos
    
    alt Es Supervisor
        AdminReservaService->>Database: SELECT escuela y facultad asignada
        Database-->>AdminReservaService: 1 Facultad y 1 Escuela
    else Es Administrador Global
        AdminReservaService->>FacultadRepository: findAll()
        FacultadRepository->>Database: SELECT * FROM facultad
        Database-->>FacultadRepository: Lista Facultades
        
        AdminReservaService->>EscuelaRepository: findAll()
        EscuelaRepository->>Database: SELECT * FROM escuela
        Database-->>EscuelaRepository: Lista Escuelas
    end
    
    AdminReservaService-->>AdminReservaController: AdminReservaFiltersResponse
    AdminReservaController-->>Frontend: HTTP 200 JSON {tipos, facultades, escuelas}
    Frontend-->>Admin: Despliega opciones en los selectores
```

---

## 3. Función: Gestionar Reserva (Aprobar / Rechazar)

### Descripción
Permite a un administrador o supervisor evaluar una reserva "Pendiente". El administrador ingresa un motivo y opcionalmente comentarios, determinando si la reserva pasa a estado "Aprobada" o "Rechazada".

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant AdminReservaController
    participant AdminReservaService
    participant ReservaRepository
    participant ReservaGestionRepository
    participant Database

    Admin->>Frontend: Clic en "Aprobar" / "Rechazar"
    Frontend->>AdminReservaController: POST /api/admin/reservas/{id}/gestionar
    
    AdminReservaController->>AdminReservaController: Valida JSON (usuarioGestionId, accion, motivo)
    AdminReservaController->>AdminReservaService: gestionarReserva(reservaId, request)
    
    AdminReservaService->>ReservaRepository: findById(reservaId)
    ReservaRepository->>Database: SELECT * FROM reserva WHERE id = ?
    Database-->>ReservaRepository: Instancia Reserva
    
    AdminReservaService->>AdminReservaService: Valida si ya tiene el estado solicitado (HTTP 409)
    
    AdminReservaService->>ReservaRepository: save(reserva con nuevo estado)
    ReservaRepository->>Database: UPDATE reserva SET estado = 'Aprobada/Rechazada' WHERE id = ?
    Database-->>ReservaRepository: OK
    
    AdminReservaService->>ReservaGestionRepository: save(nueva gestion)
    ReservaGestionRepository->>Database: INSERT INTO reserva_gestion (reservaId, usuarioGestionId, accion, motivo...)
    Database-->>ReservaGestionRepository: OK
    
    AdminReservaService->>ReservaRepository: buscarReservaPorId(reservaId) (Refrescar Data)
    ReservaRepository->>Database: SELECT * FROM reserva...
    Database-->>ReservaRepository: Reserva actualizada
    
    AdminReservaService-->>AdminReservaController: AdminReservaCardDto
    AdminReservaController-->>Frontend: HTTP 200 JSON {reserva Actualizada}
    Frontend-->>Admin: Actualiza estado en UI y muestra Toast
```
