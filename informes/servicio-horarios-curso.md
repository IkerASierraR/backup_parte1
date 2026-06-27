# Servicio de Horarios de Cursos (servicio-horarios-curso)

## Descripción
Este microservicio se enfoca en la asignación académica. Se encarga de vincular un Curso, un Docente, un Espacio Físico (Aula/Laboratorio) y un Bloque de tiempo. Es la pieza central que permite construir la malla horaria académica (el horario de clases) de la universidad.

## Arquitectura
- **Frontend:** React (Pantalla de "Gestión de Horarios Académicos").
- **Backend:** Laravel (`servicio-horarios-curso`, controladores `HorarioCursoController` y `HorarioCatalogoController`).
- **Base de Datos:** MySQL (Tablas esperadas: `horarios_cursos` y dependencias a `cursos`, `usuarios/docentes`, `espacios`, `bloques`).

---

## 1. Función: Gestión del Horario Académico (CRUD)

### Descripción
Permite listar el horario de clases, buscar un registro específico, así como crear, modificar o eliminar una asignación de clase (Curso + Docente + Espacio + Bloque).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Coordinador
    participant Frontend
    participant HorarioCursoController
    participant HorarioCursoService
    participant Database

    %% Crear Asignación
    Coordinador->>Frontend: Asigna "Matemáticas" con "Docente X" en "Aula 101", "Lunes 08:00"
    Frontend->>HorarioCursoController: POST /api/horarios {cursoId, docenteId, espacioId, bloqueId...}
    
    HorarioCursoController->>HorarioCursoController: Valida request (HorarioCursoRequest)
    HorarioCursoController->>HorarioCursoService: crear(datos)
    
    HorarioCursoService->>Database: Valida cruces (El docente ya dicta a esa hora o el aula está ocupada)
    
    alt Existe Cruce
        Database-->>HorarioCursoService: Cruce detectado
        HorarioCursoService-->>HorarioCursoController: throw Exception
        HorarioCursoController-->>Frontend: HTTP 422/400 Error
    else Todo Correcto
        HorarioCursoService->>Database: INSERT INTO horarios_cursos ...
        Database-->>HorarioCursoService: OK
        HorarioCursoService-->>HorarioCursoController: Instancia
        HorarioCursoController-->>Frontend: HTTP 201 JSON
    end
    
    %% Consultar Horario
    Coordinador->>Frontend: Ver Malla
    Frontend->>HorarioCursoController: GET /api/horarios
    HorarioCursoController->>HorarioCursoService: listar()
    HorarioCursoService->>Database: SELECT con Eager Loading (curso, docente, espacio)
    Database-->>HorarioCursoService: Lista
    HorarioCursoService-->>HorarioCursoController: Array
    HorarioCursoController-->>Frontend: HTTP 200 JSON
```

---

## 2. Función: Catálogos de Soporte

### Descripción
Para construir la malla horaria, el frontend requiere poblar los `selects` (comboboxes) con las listas maestras de Cursos, Docentes, Espacios y Bloques horarios disponibles.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Sistema
    participant Frontend
    participant HorarioCatalogoController
    participant CatalogoService
    participant Database

    Sistema->>Frontend: Carga la vista de "Nuevo Horario de Curso"
    
    par Consultas Paralelas
        Frontend->>HorarioCatalogoController: GET /api/horarios/catalogos/cursos
        HorarioCatalogoController->>CatalogoService: listarCursos()
        CatalogoService->>Database: SELECT * FROM cursos
        Database-->>CatalogoService: Lista
        CatalogoService-->>HorarioCatalogoController: Array
        HorarioCatalogoController-->>Frontend: HTTP 200 JSON
        
        Frontend->>HorarioCatalogoController: GET /api/horarios/catalogos/docentes
        HorarioCatalogoController->>CatalogoService: listarDocentes()
        CatalogoService->>Database: SELECT * FROM usuarios WHERE rol = 'docente'
        Database-->>CatalogoService: Lista
        CatalogoService-->>HorarioCatalogoController: Array
        HorarioCatalogoController-->>Frontend: HTTP 200 JSON
        
        Frontend->>HorarioCatalogoController: GET /api/horarios/catalogos/espacios
        HorarioCatalogoController->>CatalogoService: listarEspacios()
        CatalogoService->>Database: SELECT * FROM espacios
        Database-->>CatalogoService: Lista
        CatalogoService-->>HorarioCatalogoController: Array
        HorarioCatalogoController-->>Frontend: HTTP 200 JSON
        
        Frontend->>HorarioCatalogoController: GET /api/horarios/catalogos/bloques
        HorarioCatalogoController->>CatalogoService: listarBloques()
        CatalogoService->>Database: SELECT * FROM bloques_horarios
        Database-->>CatalogoService: Lista
        CatalogoService-->>HorarioCatalogoController: Array
        HorarioCatalogoController-->>Frontend: HTTP 200 JSON
    end
```
