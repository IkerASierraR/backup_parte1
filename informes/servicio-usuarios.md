# Servicio de Usuarios (servicio-usuarios)

## Descripción
Este microservicio es responsable de la gestión integral de todos los actores del sistema (Estudiantes, Docentes y Administrativos). Controla el ciclo de vida de los usuarios (CRUD: crear, leer, actualizar, eliminar/desactivar), sus perfiles específicos (código de estudiante, tipo de contrato del docente, etc.) y su relación con la tabla base `usuario` y `usuario_auth` (credenciales).

## Arquitectura
- **Frontend:** React (Pantallas del módulo "Gestión de Usuarios" en el portal de Administrador).
- **Backend:** Laravel (`servicio-usuarios`, controladores `EstudianteController`, `DocenteController`, `AdministrativoController`).
- **Base de Datos:** MySQL (Tablas: `usuario`, `usuario_auth`, `estudiante`, `docente`, `administrativo`).

---

## 1. Función: Gestión de Estudiantes (CRUD)

### Descripción
Permite a la administración visualizar la lista de estudiantes, registrar nuevos (creando simultáneamente su registro en `usuario`, `usuario_auth` y `estudiante`), actualizar su información o darlos de baja (cambiando su estado a inactivo).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant EstudianteController
    participant Database

    %% Listar
    Admin->>Frontend: Abre módulo "Estudiantes"
    Frontend->>EstudianteController: GET /api/estudiantes
    EstudianteController->>Database: SELECT * FROM estudiante WITH (usuario, auth...)
    Database-->>EstudianteController: Lista de estudiantes
    EstudianteController-->>Frontend: HTTP 200 JSON
    
    %% Crear
    Admin->>Frontend: Llena formulario "Nuevo Estudiante"
    Frontend->>EstudianteController: POST /api/estudiantes {nombre, codigo, correo, password...}
    
    EstudianteController->>Database: BEGIN TRANSACTION
    EstudianteController->>Database: INSERT INTO usuario (Rol: 2)
    Database-->>EstudianteController: usuarioId
    EstudianteController->>Database: INSERT INTO usuario_auth (Password encriptado)
    EstudianteController->>Database: INSERT INTO estudiante (codigo, escuelaId)
    
    alt Error en algún paso
        EstudianteController->>Database: ROLLBACK
        EstudianteController-->>Frontend: HTTP 500
    else Todo OK
        EstudianteController->>Database: COMMIT
        EstudianteController-->>Frontend: HTTP 201 JSON (Datos del nuevo estudiante)
    end
```

---

## 2. Función: Gestión de Docentes (CRUD)

### Descripción
Similar al flujo de estudiantes, pero adaptado a la tabla `docente`, manejando campos específicos como el tipo de contrato, código de docente y especialidad.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant DocenteController
    participant Database

    Admin->>Frontend: Editar datos de un Docente
    Frontend->>DocenteController: PUT /api/docentes/{id} {tipoContrato, celular...}
    
    DocenteController->>Database: BEGIN TRANSACTION
    DocenteController->>Database: UPDATE docente SET tipoContrato = ? WHERE id = ?
    DocenteController->>Database: UPDATE usuario SET celular = ? WHERE idUsuario = ?
    
    alt Cambio de Credenciales
        DocenteController->>Database: UPDATE usuario_auth SET Password = ? (opcional)
    end
    
    DocenteController->>Database: COMMIT
    DocenteController-->>Frontend: HTTP 200 JSON (Docente Actualizado)
```

---

## 3. Función: Suspensión Lógica de Usuarios (Baja)

### Descripción
El sistema no elimina registros físicamente (Hard Delete) por motivos de auditoría y relaciones con tablas históricas (reservas). En su lugar, se actualiza la bandera `Estado` de la tabla `usuario` a 0 (Inactivo), lo que bloquea el login de dicho usuario.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant AdministrativoController
    participant Database

    Admin->>Frontend: Clic en "Dar de baja" al Administrativo #45
    Frontend->>AdministrativoController: DELETE /api/administrativos/45
    
    AdministrativoController->>AdministrativoController: Llama a estado(activo: false)
    
    AdministrativoController->>Database: SELECT * FROM administrativo WHERE id = 45
    Database-->>AdministrativoController: Administrativo
    
    AdministrativoController->>Database: UPDATE usuario SET Estado = 0 WHERE idUsuario = ?
    Database-->>AdministrativoController: OK
    
    AdministrativoController-->>Frontend: HTTP 200 JSON (Estado actualizado)
```
