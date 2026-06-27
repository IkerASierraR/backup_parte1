# Servicio de Canales (servicio-canales)

## Descripción
Este microservicio provee la funcionalidad principal para una plataforma de comunicación estilo chat o foros (similar a Slack/Discord). Permite gestionar canales (públicos o privados), organizar discusiones en "temas" (threads/hilos), enviar mensajes con soporte de respuestas e imágenes, reaccionar a mensajes, buscar usuarios para invitar a canales, y generar previsualizaciones de enlaces (URL unfurling).

## Arquitectura
- **Frontend:** React (Llamadas a los endpoints de canales, websockets no evidenciados en las rutas HTTP).
- **Backend:** Laravel (`servicio-canales` con controladores dedicados: `CanalController`, `TemaController`, `MensajeController`, `ReaccionController`, `PreviewController`, `UsuarioController`).
- **Base de Datos:** MySQL (Tablas: `canales`, `canal_temas`, `canal_mensajes`, `canal_usuarios`, `canal_mensaje_reacciones`, `usuarios`).

---

## 1. Función: Gestión de Canales

### Descripción
Crea, lista, actualiza y elimina canales. Un canal puede ser público o privado, y agrupa a varios usuarios (miembros).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant CanalController
    participant Database

    Usuario->>Frontend: Clic en Crear Canal
    Frontend->>CanalController: POST /api/canales {nombre, tipo...}
    
    CanalController->>CanalController: Valida request
    CanalController->>Database: INSERT INTO canales (nombre, tipo, estado...)
    Database-->>CanalController: IdCanal generado
    
    CanalController->>Database: INSERT INTO canal_usuarios (usuarioId = creador)
    Database-->>CanalController: Miembro añadido
    
    CanalController-->>Frontend: HTTP 201 JSON (CanalDTO)
```

---

## 2. Función: Gestión de Temas (Hilos)

### Descripción
Dentro de un canal, la conversación se puede organizar en "temas". Permite CRUD de temas asociados a un `idCanal`.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant TemaController
    participant Database

    Usuario->>Frontend: Agrega un Tema al Canal
    Frontend->>TemaController: POST /api/canales/{idCanal}/temas {nombre}
    
    TemaController->>Database: SELECT * FROM canales WHERE id = ?
    
    alt Canal no existe
        Database-->>TemaController: null
        TemaController-->>Frontend: HTTP 404 Not Found
    else Canal existe
        Database-->>TemaController: Canal
        TemaController->>Database: INSERT INTO canal_temas (IdCanal, Nombre, Orden)
        Database-->>TemaController: Tema creado
        TemaController-->>Frontend: HTTP 201 JSON
    end
```

---

## 3. Función: Mensajería y Respuestas

### Descripción
Permite a los usuarios enviar mensajes a un tema específico. Un mensaje puede ser una respuesta a otro (`idMensajeRespuesta`) e incluir una imagen adjunta (`imagenUrl`). El sistema carga automáticamente el autor y el mensaje original al que se responde.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant MensajeController
    participant Database

    Usuario->>Frontend: Escribe y envía mensaje
    Frontend->>MensajeController: POST /api/canales/{idCanal}/temas/{idTema}/mensajes
    
    MensajeController->>Database: Valida existencia de Canal y Tema
    Database-->>MensajeController: OK
    
    MensajeController->>Database: INSERT INTO canal_mensajes (contenido, usuarioId, respuestaA...)
    Database-->>MensajeController: Mensaje creado
    
    MensajeController->>Database: SELECT con Eager Loading (usuario, respuestaA)
    Database-->>MensajeController: Mensaje hidratado
    
    MensajeController->>MensajeController: mapear(mensaje)
    MensajeController-->>Frontend: HTTP 201 JSON
    Frontend-->>Usuario: Actualiza UI del chat
```

---

## 4. Función: Previsualización de Enlaces (URL Unfurling)

### Descripción
Cuando un usuario pega una URL en el chat, el Frontend llama a este endpoint para obtener metadatos de la página (título, descripción, imagen OpenGraph) y generar una tarjeta de previsualización rica (estilo Twitter Cards).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Frontend
    participant PreviewController
    participant ExternalWebsite

    Frontend->>PreviewController: GET /api/preview?url=https://...
    
    PreviewController->>PreviewController: Valida URL (http/https)
    
    PreviewController->>ExternalWebsite: file_get_contents(URL) con timeout
    
    alt Error de conexión
        ExternalWebsite-->>PreviewController: false
        PreviewController-->>Frontend: HTTP 422 JSON {error}
    else Conexión exitosa
        ExternalWebsite-->>PreviewController: HTML puro (limitado a 60KB)
        PreviewController->>PreviewController: mb_convert_encoding(UTF-8)
        
        PreviewController->>PreviewController: Parsear meta tags (og:title, og:image, description)
        
        PreviewController-->>Frontend: HTTP 200 JSON {title, description, image, url, siteName}
    end
```
