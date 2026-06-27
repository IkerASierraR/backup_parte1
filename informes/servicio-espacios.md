# Servicio de Espacios (servicio-espacios)

## Descripción
Este microservicio administra el catálogo físico de la universidad (Aulas, Laboratorios, Auditorios, Canchas Deportivas, etc.). Permite registrar nuevos espacios, modificarlos, listarlos, eliminarlos y consultar las escuelas a las que pertenecen, sirviendo como catálogo base para el sistema de reservas.

## Arquitectura
- **Frontend:** React (Llamadas CRUD básicas desde el panel de administración).
- **Backend:** Laravel (`servicio-espacios`, controlador `EspacioController`).
- **Base de Datos:** MySQL (Tablas: `espacios`, `escuelas`).

---

## 1. Función: CRUD de Espacios (Listar, Obtener, Crear, Actualizar, Eliminar)

### Descripción
El flujo estándar REST para gestionar los espacios universitarios.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant EspacioController
    participant EspacioService
    participant Database

    %% Leer Todos
    Admin->>Frontend: Abre "Gestión de Espacios"
    Frontend->>EspacioController: GET /api/espacios
    EspacioController->>EspacioService: listar()
    EspacioService->>Database: SELECT * FROM espacios
    Database-->>EspacioService: Lista de Espacios
    EspacioService-->>EspacioController: Array de Espacios
    EspacioController-->>Frontend: HTTP 200 JSON
    
    %% Leer Escuelas
    Frontend->>EspacioController: GET /api/espacios/escuelas
    EspacioController->>Database: SELECT * FROM escuelas
    Database-->>EspacioController: Lista de Escuelas (EscuelaResource)
    EspacioController-->>Frontend: HTTP 200 JSON
    
    %% Crear
    Admin->>Frontend: Llena formulario y guarda
    Frontend->>EspacioController: POST /api/espacios {nombre, tipo, capacidad...}
    EspacioController->>EspacioController: Valida request (EspacioRequest)
    EspacioController->>EspacioService: crear(datos)
    EspacioService->>Database: INSERT INTO espacios ...
    Database-->>EspacioService: Espacio Creado
    EspacioService-->>EspacioController: Instancia
    EspacioController-->>Frontend: HTTP 201 Created
    
    %% Actualizar
    Admin->>Frontend: Edita un espacio existente
    Frontend->>EspacioController: PUT /api/espacios/{id} {datos}
    EspacioController->>EspacioService: actualizar(id, datos)
    EspacioService->>Database: UPDATE espacios SET ... WHERE id = ?
    Database-->>EspacioService: Espacio Actualizado
    EspacioService-->>EspacioController: Instancia
    EspacioController-->>Frontend: HTTP 200 JSON
    
    %% Eliminar
    Admin->>Frontend: Elimina un espacio
    Frontend->>EspacioController: DELETE /api/espacios/{id}
    EspacioController->>EspacioService: eliminar(id)
    EspacioService->>Database: DELETE FROM espacios WHERE id = ?
    Database-->>EspacioService: OK
    EspacioService-->>EspacioController: void
    EspacioController-->>Frontend: HTTP 204 No Content
```
