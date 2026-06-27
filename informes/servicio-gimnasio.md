# Servicio de Gimnasio (servicio-gimnasio)

## Descripción
Este microservicio gestiona el control de asistencia y tiempo de uso del gimnasio universitario. Permite a los usuarios (estudiantes/docentes) registrar su hora de entrada y de salida, consultar si actualmente tienen una sesión activa dentro del recinto, y a los administradores les permite listar el historial general de asistencias para control de aforo y reportes.

## Arquitectura
- **Frontend:** React (Aplicación móvil o portal web para escanear QR de entrada/salida o marcar digitalmente).
- **Backend:** Laravel (`servicio-gimnasio`, controlador `GimnasioController`, servicio `GimnasioService`).
- **Base de Datos:** MySQL (Tablas esperadas: `gimnasio_asistencias`).

---

## 1. Función: Registro de Ingreso

### Descripción
Registra la marca de tiempo de entrada de un usuario al gimnasio. Valida que el usuario no tenga ya una sesión activa (es decir, que haya ingresado pero no marcado su salida).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant GimnasioController
    participant GimnasioService
    participant Database

    Usuario->>Frontend: Marca "Ingreso al Gimnasio"
    Frontend->>GimnasioController: POST /api/ingreso {usuarioId}
    
    GimnasioController->>GimnasioService: registrarIngreso(usuarioId)
    
    GimnasioService->>Database: Validar si existe sesión sin hora_salida
    
    alt Ya está dentro del gimnasio
        Database-->>GimnasioService: Sesión activa encontrada
        GimnasioService-->>GimnasioController: throw LogicException
        GimnasioController-->>Frontend: HTTP 409 Conflict
    else Puede ingresar
        Database-->>GimnasioService: Ninguna sesión activa
        GimnasioService->>Database: INSERT INTO gimnasio_asistencias (usuarioId, hora_ingreso = NOW())
        Database-->>GimnasioService: OK
        GimnasioService-->>GimnasioController: Asistencia registrada
        GimnasioController-->>Frontend: HTTP 201 Created
    end
```

---

## 2. Función: Registro de Salida

### Descripción
Registra la marca de tiempo de salida de un usuario. Requiere que el usuario tenga una sesión activa previamente registrada el mismo día.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant GimnasioController
    participant GimnasioService
    participant Database

    Usuario->>Frontend: Marca "Salida del Gimnasio"
    Frontend->>GimnasioController: POST /api/salida {usuarioId}
    
    GimnasioController->>GimnasioService: registrarSalida(usuarioId)
    
    GimnasioService->>Database: Buscar sesión activa (hora_salida IS NULL)
    
    alt No está en el gimnasio
        Database-->>GimnasioService: null
        GimnasioService-->>GimnasioController: throw InvalidArgumentException
        GimnasioController-->>Frontend: HTTP 404 Not Found
    else Salida Exitosa
        Database-->>GimnasioService: Sesión activa
        GimnasioService->>Database: UPDATE gimnasio_asistencias SET hora_salida = NOW() WHERE id = ?
        Database-->>GimnasioService: OK
        GimnasioService-->>GimnasioController: Asistencia finalizada
        GimnasioController-->>Frontend: HTTP 200 JSON
    end
```

---

## 3. Función: Consultar Estado de Sesión Actual

### Descripción
Endpoint utilizado para que la Interfaz de Usuario determine qué botón mostrar ("Registrar Ingreso" o "Registrar Salida") consultando si el usuario está actualmente dentro del gimnasio.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Frontend
    participant GimnasioController
    participant GimnasioService
    participant Database

    Frontend->>GimnasioController: GET /api/estado/{usuarioId}
    
    GimnasioController->>GimnasioService: estadoSesion(usuarioId)
    GimnasioService->>Database: SELECT * FROM gimnasio_asistencias WHERE usuarioId = ? AND hora_salida IS NULL
    
    alt Tiene sesión activa
        Database-->>GimnasioService: Registro encontrado
        GimnasioService-->>GimnasioController: { enGimnasio: true, horaIngreso: ... }
    else No está en el gimnasio
        Database-->>GimnasioService: null
        GimnasioService-->>GimnasioController: { enGimnasio: false }
    end
    
    GimnasioController-->>Frontend: HTTP 200 JSON
```

---

## 4. Función: Listar Asistencias (Historial)

### Descripción
Endpoint administrativo para listar todas las asistencias registradas, útil para generar reportes de horas pico y controlar el aforo histórico.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant GimnasioController
    participant GimnasioService
    participant Database

    Admin->>Frontend: Abre "Reporte de Gimnasio"
    Frontend->>GimnasioController: GET /api/asistencias
    
    GimnasioController->>GimnasioService: listarAsistencias()
    GimnasioService->>Database: SELECT * FROM gimnasio_asistencias ORDER BY hora_ingreso DESC
    Database-->>GimnasioService: Historial completo
    
    GimnasioService-->>GimnasioController: Array
    GimnasioController-->>Frontend: HTTP 200 JSON
```
