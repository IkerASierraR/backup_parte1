# Servicio de Reservas (servicio-reserva)

## Descripción
Este es el microservicio central o "core" de todo el ecosistema IntegraUpt. Gestiona el proceso completo de apartar un ambiente físico (laboratorio, salón especial, auditorio) por parte de un usuario (generalmente docentes para sus cursos). Involucra catálogos básicos (facultades, escuelas), espacios físicos, y las reservas en sí, coordinándose estrechamente con el servicio QR para generar los pases de acceso.

## Arquitectura
- **Frontend:** React (Pantalla "Mis Reservas", "Crear Reserva" y calendarios de disponibilidad).
- **Backend:** Laravel (`servicio-reserva`, controladores `ReservaController`, `EspacioController`, `CatalogoController`).
- **Base de Datos:** MySQL (Tablas: `reserva`, `espacio`, `cursos`, `bloqueshorarios`).

---

## 1. Función: Creación de una Reserva (Docente/Usuario)

### Descripción
Un usuario solicita un espacio físico para una fecha y bloque horario determinado, vinculándolo al curso que dictará. El sistema valida cruces y, si se aprueba la reserva (automáticamente o mediante reglas de negocio), se coordina la generación del pase QR.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant ReservaController
    participant ReservaService
    participant QRService(Externo)
    participant Database

    Usuario->>Frontend: Completa formulario de Reserva
    Frontend->>ReservaController: POST /api/reservas {espacioId, bloqueId, fecha, cursoId...}
    
    ReservaController->>ReservaService: crearReserva(datos)
    
    ReservaService->>Database: Valida disponibilidad (Cruce de horarios / Aforo)
    
    alt Espacio No Disponible
        Database-->>ReservaService: Ya reservado
        ReservaService-->>ReservaController: throw LogicException
        ReservaController-->>Frontend: HTTP 409 Conflict
    else Válido
        ReservaService->>Database: INSERT INTO reserva (Estado: Aprobada/Pendiente)
        Database-->>ReservaService: Reserva Creada
        
        %% Integración (Acoplamiento de lógica interna o llamada a API)
        ReservaService->>QRService(Externo): Solicita generación de QR (token)
        QRService(Externo)-->>ReservaService: UUID / Base64
        
        ReservaService-->>ReservaController: Array {reserva, qr}
        ReservaController-->>Frontend: HTTP 201 JSON
    end
```

---

## 2. Función: Consultar Catálogo de Espacios y Bloques

### Descripción
Antes de poder reservar, el frontend necesita llenar los campos desplegables (`selects`) con los laboratorios existentes y saber en qué bloques horarios atienden (ej. 8:00 - 10:00).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Sistema
    participant Frontend
    participant EspacioController
    participant EspacioService
    participant Database

    Sistema->>Frontend: Abre "Nueva Reserva"
    
    par
        Frontend->>EspacioController: GET /api/espacios?escuelaId=...
        EspacioController->>EspacioService: listarActivosPorEscuela()
        EspacioService->>Database: SELECT * FROM espacio
        Database-->>EspacioService: Lista
        EspacioService-->>EspacioController: Array
        EspacioController-->>Frontend: HTTP 200 JSON
        
        Frontend->>EspacioController: GET /api/espacios/{espacioId}/bloques
        EspacioController->>EspacioService: listarBloquesPorEspacio()
        EspacioService->>Database: SELECT * FROM bloqueshorarios
        Database-->>EspacioService: Bloques
        EspacioService-->>EspacioController: Array
        EspacioController-->>Frontend: HTTP 200 JSON
    end
```

---

## 3. Función: Gestión de "Mis Reservas" y Pases QR

### Descripción
El usuario puede visualizar todas sus reservas pasadas y futuras. Desde esta pantalla, puede solicitar la visualización de su pase QR para presentarlo a la entrada del laboratorio.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant ReservaController
    participant ReservaService
    participant Database

    %% Listar Reservas
    Usuario->>Frontend: Va a "Historial de Reservas"
    Frontend->>ReservaController: GET /api/reservas/usuario/{usuarioId}
    ReservaController->>ReservaService: listarPorUsuario()
    ReservaService->>Database: SELECT * FROM reserva WHERE usuario = ?
    Database-->>ReservaService: Lista
    ReservaService-->>ReservaController: Array
    ReservaController-->>Frontend: HTTP 200 JSON
    
    %% Ver Pase QR
    Usuario->>Frontend: Clic en "Ver Mi Código QR" en la reserva #150
    Frontend->>ReservaController: GET /api/reservas/150/qr
    ReservaController->>ReservaService: obtenerReservaConQr(150)
    ReservaService->>Database: SELECT de reserva + reserva_qr (Relación)
    Database-->>ReservaService: Data y Token QR
    ReservaService-->>ReservaController: { reserva, qrBase64 }
    ReservaController-->>Frontend: HTTP 200 JSON
    Frontend-->>Usuario: Muestra Pop-up con el QR y los datos
```
