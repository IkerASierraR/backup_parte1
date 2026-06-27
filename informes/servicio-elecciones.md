# Servicio de Elecciones (servicio-elecciones)

## Descripción
Este microservicio gestiona los procesos electorales universitarios (Asamblea Universitaria, Consejo Universitario y Consejo de Facultad). Permite a los administradores crear elecciones, registrar agrupaciones políticas (partidos), iniciar un proceso (activar) y contabilizar resultados en tiempo real. Por otro lado, permite a los estudiantes emitir un voto seguro (vinculado a su ID), generar un código de comprobación y consultar si ya votaron.

## Arquitectura
- **Frontend:** React (Pantallas de votación electrónica y dashboard de resultados).
- **Backend:** Laravel (`servicio-elecciones`, controlador `ElectionController`).
- **Base de Datos:** MySQL (Tablas `elections`, `parties`, `votes`).

---

## 1. Función: Votación de Estudiantes

### Descripción
Un estudiante consulta la elección activa y emite su voto para 3 cargos distintos (Asamblea, Consejo Universitario, Consejo de Facultad). El sistema genera un código de verificación único para el estudiante.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Estudiante
    participant Frontend
    participant ElectionController
    participant Database

    Estudiante->>Frontend: Ingresa a "Centro de Votación"
    Frontend->>ElectionController: GET /elecciones/activas
    ElectionController->>Database: SELECT * FROM elections WHERE is_active = 1
    Database-->>ElectionController: Elección Activa + Partidos
    ElectionController-->>Frontend: HTTP 200 JSON
    
    Estudiante->>Frontend: Selecciona listas y pulsa Votar
    Frontend->>ElectionController: POST /elecciones/{id}/votar {student_id, faculty, votos...}
    
    ElectionController->>ElectionController: Valida request (existencia de partidos)
    
    ElectionController->>Database: SELECT * FROM elections WHERE id = ?
    Database-->>ElectionController: Elección
    
    alt Elección inactiva
        ElectionController-->>Frontend: HTTP 400 Bad Request
    else Elección Activa
        ElectionController->>ElectionController: Genera verification_code (Str::random)
        ElectionController->>Database: INSERT INTO votes (student_id, faculty, asamblea_party_id..., verification_code, ip)
        Database-->>ElectionController: Voto guardado
        
        ElectionController-->>Frontend: HTTP 200 JSON {message, verification_code}
        Frontend-->>Estudiante: Muestra constancia de voto y código
    end
```

---

## 2. Función: Gestión de Elecciones y Partidos (Admin)

### Descripción
Permite a los administradores crear procesos electorales, añadir partidos políticos y decidir qué elección está activa (solo puede haber una activa a la vez).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant ElectionController
    participant Database

    Admin->>Frontend: Crea nueva elección y añade partidos
    Frontend->>ElectionController: POST /admin/elecciones {title, dates}
    ElectionController->>Database: INSERT INTO elections...
    Database-->>ElectionController: Elección creada
    ElectionController-->>Frontend: HTTP 201 Created
    
    Frontend->>ElectionController: POST /admin/elecciones/{id}/partidos {name}
    ElectionController->>Database: INSERT INTO parties (election_id, name)
    Database-->>ElectionController: OK
    ElectionController-->>Frontend: HTTP 201 Created
    
    Admin->>Frontend: Activa la elección
    Frontend->>ElectionController: PATCH /admin/elecciones/{id}/activar
    
    ElectionController->>Database: UPDATE elections SET is_active = 0 WHERE id != ?
    ElectionController->>Database: UPDATE elections SET is_active = NOT is_active WHERE id = ?
    Database-->>ElectionController: OK
    
    ElectionController-->>Frontend: HTTP 200 JSON
```

---

## 3. Función: Resultados en Tiempo Real (Admin)

### Descripción
Calcula la suma total de votos y los porcentajes por cada agrupación política, agrupados por Asamblea, Consejo Universitario y Consejo de Facultad (este último desglosado por facultad). También incluye votos en blanco.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant ElectionController
    participant Database

    Admin->>Frontend: Accede al Dashboard de Resultados
    Frontend->>ElectionController: GET /admin/elecciones/{id}/resultados
    
    ElectionController->>Database: SELECT * FROM elections (con Partidos)
    ElectionController->>Database: SELECT COUNT(*) FROM votes WHERE election_id = ?
    
    ElectionController->>Database: GROUP BY asamblea_party_id (COUNT)
    Database-->>ElectionController: Votos por partido (Asamblea)
    
    ElectionController->>Database: GROUP BY consejo_uni_party_id (COUNT)
    Database-->>ElectionController: Votos por partido (Consejo Uni)
    
    ElectionController->>Database: DISTINCT faculty FROM votes
    Database-->>ElectionController: Lista de facultades participantes
    
    loop Por cada facultad
        ElectionController->>Database: GROUP BY consejo_fac_party_id WHERE faculty = ?
        Database-->>ElectionController: Votos de la facultad
    end
    
    ElectionController->>ElectionController: Agrega "Voto en Blanco" y calcula porcentajes (%)
    
    ElectionController-->>Frontend: HTTP 200 JSON {total_votes, results: {asamblea, consejo_uni, consejo_fac}}
    Frontend-->>Admin: Dibuja gráficos estadísticos
```
