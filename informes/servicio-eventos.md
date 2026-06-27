# Servicio de Eventos (servicio-eventos)

## Descripción
Este microservicio gestiona el ciclo completo de eventos universitarios (conferencias, talleres, seminarios). Permite crear eventos, definir su alcance (facultad, escuela o general), gestionar inscripciones de estudiantes/docentes, realizar control de asistencia (check-in con QR) y emitir y verificar certificados digitales.

## Arquitectura
- **Frontend:** React (Gestión de eventos para Admin, Catálogo y Mis Eventos para Usuarios).
- **Backend:** Laravel (`servicio-eventos` con controladores: `EventoController`, `InscripcionController`, `CertificadoController`, `CatalogoController`).
- **Base de Datos:** MySQL (Tablas principales: `eventos`, `evento_inscripciones`, `evento_certificados`).

---

## 1. Función: Gestión de Eventos (CRUD y Estados)

### Descripción
Permite a los administradores crear eventos, subir su imagen (banner), actualizar su información y cambiar su estado a lo largo de su ciclo de vida (`borrador`, `publicado`, `en_curso`, `finalizado`, `cancelado`).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant EventoController
    participant EventoService
    participant Database

    Admin->>Frontend: Completa datos del evento y sube banner
    Frontend->>EventoController: POST /api/eventos (Multipart)
    
    EventoController->>EventoController: aPascalCase(request)
    
    opt Tiene Imagen
        EventoController->>EventoController: guardarImagen()
        EventoController->>Servidor: Guarda en /uploads/eventos/uuid.ext
    end
    
    EventoController->>EventoService: crear(datos)
    EventoService->>Database: INSERT INTO eventos ...
    Database-->>EventoService: OK
    EventoService-->>EventoController: Instancia
    EventoController-->>Frontend: HTTP 201 Created
    
    Admin->>Frontend: Cambia estado a "publicado"
    Frontend->>EventoController: PATCH /api/eventos/{id}/estado {estado: 'publicado'}
    EventoController->>EventoService: cambiarEstado(id, 'publicado')
    EventoService->>Database: UPDATE eventos SET Estado = 'publicado' WHERE ...
    Database-->>EventoService: OK
    EventoService-->>EventoController: Evento actualizado
    EventoController-->>Frontend: HTTP 200 JSON
```

---

## 2. Función: Inscripción a Eventos

### Descripción
Un usuario puede inscribirse a un evento (si hay cupos disponibles). Al inscribirse, se genera automáticamente un Código QR único asociado a esa inscripción.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant InscripcionController
    participant InscripcionService
    participant Database

    Usuario->>Frontend: Clic en "Inscribirme"
    Frontend->>InscripcionController: POST /api/eventos/{idEvento}/inscripciones {usuarioId}
    
    InscripcionController->>InscripcionService: inscribir(idEvento, usuarioId)
    
    InscripcionService->>Database: Validar cupos y estado del evento
    
    alt Sin Cupos o Evento Cerrado
        InscripcionService-->>InscripcionController: throw InvalidArgumentException
        InscripcionController-->>Frontend: HTTP 422 Unprocessable Entity
    else Hay Cupo
        InscripcionService->>Database: INSERT INTO evento_inscripciones (idEvento, idUsuario, codigoQr...)
        Database-->>InscripcionService: OK
        InscripcionService-->>InscripcionController: Inscripcion
        InscripcionController-->>Frontend: HTTP 201 JSON
    end
```

---

## 3. Función: Control de Asistencia (Check-in con QR)

### Descripción
El día del evento, los administradores escanean el código QR de los asistentes para validar su ingreso (pasa de estado "inscrito" a "asistio").

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Organizador
    participant Frontend
    participant InscripcionController
    participant InscripcionService
    participant Database

    Organizador->>Frontend: Escanea QR de entrada
    Frontend->>InscripcionController: POST /api/eventos/{id}/checkin {codigoQr}
    
    InscripcionController->>InscripcionService: checkin(codigoQr)
    
    InscripcionService->>Database: SELECT * FROM evento_inscripciones WHERE codigoQr = ?
    Database-->>InscripcionService: Inscripcion
    
    alt QR inválido
        InscripcionService-->>InscripcionController: throw RuntimeException
        InscripcionController-->>Frontend: HTTP 404 Not Found
    else QR ya escaneado o evento cancelado
        InscripcionService-->>InscripcionController: throw InvalidArgumentException
        InscripcionController-->>Frontend: HTTP 422 Unprocessable Entity
    else Check-in Exitoso
        InscripcionService->>Database: UPDATE evento_inscripciones SET estado = 'asistio' WHERE ...
        Database-->>InscripcionService: OK
        InscripcionService-->>InscripcionController: Inscripcion
        InscripcionController-->>Frontend: HTTP 200 JSON
    end
```

---

## 4. Función: Verificación de Certificados

### Descripción
Valida la autenticidad de un certificado emitido al finalizar el evento mediante su `idInscripcion`.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Externo
    participant Frontend
    participant CertificadoController
    participant Database

    Externo->>Frontend: Lee QR del certificado
    Frontend->>CertificadoController: GET /api/certificados/verificar/{idInscripcion}
    
    CertificadoController->>Database: SELECT * FROM evento_certificados WHERE IdInscripcion = ? (con Eager Loading)
    
    alt Certificado No Existe
        Database-->>CertificadoController: null
        CertificadoController-->>Frontend: HTTP 404 JSON {valido: false}
    else Certificado Existe
        Database-->>CertificadoController: Certificado + Usuario + Evento
        CertificadoController-->>Frontend: HTTP 200 JSON {valido: true, fechaEmision, usuarioNombre, eventoTitulo...}
    end
```
