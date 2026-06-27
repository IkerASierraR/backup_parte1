# Servicio de Olimpiadas Universitarias (servicio-olimpiadas)

## Descripción
Este microservicio gestiona el evento anual (o semestral) de las Olimpiadas Interfacultades de la universidad. Cubre desde la definición de disciplinas deportivas (fútbol, básquet, ajedrez, e-sports), la creación de "Ediciones" (Olimpiadas 2026), el proceso de inscripción de estudiantes por facultad, hasta la gestión de fixtures (partidos), tablas de posiciones, medalleros y una sección de blog (posts) para noticias del evento.

## Arquitectura
- **Frontend:** React (Sección "Olimpiadas" con portal de noticias, fixture en vivo, medallero y panel de inscripción).
- **Backend:** Laravel (`servicio-olimpiadas`, múltiples controladores: `EdicionController`, `DisciplinaController`, `InscripcionController`, `ResultadoController`, `PostController`).
- **Base de Datos:** MySQL (Extenso modelo de datos que cruza facultades, estudiantes, disciplinas, partidos y resultados).

---

## 1. Función: Gestión de la Edición Olímpica (Admin)

### Descripción
Un administrador crea una nueva "Edición" (ej. "Olimpiadas de Invierno 2026"), vincula las disciplinas deportivas que se jugarán en esa edición, y controla el ciclo de vida del evento (Abre/cierra inscripciones, inicia los juegos, finaliza).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant EdicionController
    participant EdicionService
    participant Database

    Admin->>Frontend: Crea Nueva Edición
    Frontend->>EdicionController: POST /api/ediciones {nombre, fechas...}
    EdicionController->>EdicionService: crear(datos)
    EdicionService->>Database: INSERT INTO olimpiada_edicion ...
    Database-->>EdicionService: Edición creada
    EdicionService-->>EdicionController: OK
    EdicionController-->>Frontend: HTTP 201 JSON
    
    Admin->>Frontend: Añade "Futsal" a la edición
    Frontend->>EdicionController: POST /api/ediciones/{id}/disciplinas {disciplinaId, cupos, reglas...}
    EdicionController->>EdicionService: vincularDisciplina(datos)
    EdicionService->>Database: INSERT INTO olimpiada_edicion_disciplinas
    Database-->>EdicionService: OK
    
    Admin->>Frontend: Clic en "Abrir Inscripciones"
    Frontend->>EdicionController: PATCH /api/ediciones/{id}/inscripcion/abrir
    EdicionController->>EdicionService: abrirInscripcion(id)
    EdicionService->>Database: UPDATE estado = 'inscripcion_abierta'
    Database-->>EdicionService: OK
```

---

## 2. Función: Inscripción de Deportistas

### Descripción
Los estudiantes pueden inscribirse a las disciplinas habilitadas para su facultad durante el período abierto de inscripciones.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Estudiante
    participant Frontend
    participant InscripcionController
    participant InscripcionService
    participant Database

    Estudiante->>Frontend: Selecciona "Futsal" y pulsa "Inscribirme"
    Frontend->>InscripcionController: POST /api/inscripciones {edicionDisciplinaId, usuarioId}
    
    InscripcionController->>InscripcionService: inscribir(datos)
    
    InscripcionService->>Database: Verifica cupos de su facultad y estado de edición
    
    alt Cupos Llenos o Edición Cerrada
        Database-->>InscripcionService: Error de Validación
        InscripcionService-->>InscripcionController: throw LogicException
        InscripcionController-->>Frontend: HTTP 409 Conflict
    else Válido
        InscripcionService->>Database: INSERT INTO olimpiada_inscripciones
        Database-->>InscripcionService: Inscrito
        InscripcionService-->>InscripcionController: OK
        InscripcionController-->>Frontend: HTTP 201 JSON
    end
```

---

## 3. Función: Fixtures y Tablas de Resultados en Vivo

### Descripción
Registra los resultados de los partidos disputados (fixture), tabla de posiciones general por deporte y la lista de anotadores (goleadores). Se usa para generar el medallero.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Juez/Admin
    participant Frontend
    participant ResultadoController
    participant ResultadoService
    participant Database

    Juez/Admin->>Frontend: Registra resultado: Facultad A (3) vs Facultad B (1)
    Frontend->>ResultadoController: POST /api/resultados {facultadLocalId, facultadVisitanteId, puntajeLocal...}
    
    ResultadoController->>ResultadoService: crear(datos)
    ResultadoService->>Database: INSERT INTO olimpiada_resultados
    
    ResultadoService->>Database: Calcula y UPDATE olimpiada_participacion_facultad (Suma Puntos, PG, PP, PE)
    Database-->>ResultadoService: Tablas actualizadas
    
    ResultadoService-->>ResultadoController: Resultado Registrado
    ResultadoController-->>Frontend: HTTP 201 JSON
    
    %% Alguien consulta el Medallero
    actor Usuario
    Usuario->>Frontend: Ve Medallero de la Edición
    Frontend->>EdicionController: GET /api/ediciones/{id}/medallero
    EdicionController->>Database: Agrupa oros, platas, bronces por Facultad
    Database-->>EdicionController: Medallero
    EdicionController-->>Frontend: HTTP 200 JSON
```

---

## 4. Función: Blog de Noticias (Posts)

### Descripción
Mini-foro integrado donde la organización pública anuncios, fotos de los ganadores o comunicados, y los usuarios pueden dejar comentarios.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    actor Usuario
    participant Frontend
    participant PostController
    participant Database

    Admin->>Frontend: Crea Noticia "Ganadores 100m Planos"
    Frontend->>PostController: POST /api/posts {titulo, contenido, imagenUrl, edicionId}
    PostController->>Database: INSERT INTO olimpiada_posts
    Database-->>PostController: OK
    PostController-->>Frontend: HTTP 201
    
    Usuario->>Frontend: Lee la noticia y comenta "Felicidades!"
    Frontend->>PostController: POST /api/posts/{id}/comentarios {contenido}
    PostController->>Database: INSERT INTO olimpiada_comentarios
    Database-->>PostController: OK
    PostController-->>Frontend: HTTP 201 JSON (Comentario adjuntado)
```
