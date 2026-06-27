# Servicio de Autenticación (servicio-login)

## Descripción
Este microservicio gestiona la identidad, el inicio de sesión y el control de sesiones de los usuarios dentro de IntegraUpt. Provee autenticación local mediante credenciales (Código/Email y Contraseña) y también está preparado para delegación de identidad (SSO) mediante Google OAuth para cuentas institucionales. Genera y administra los tokens de sesión utilizados por el frontend para consumir el resto de servicios.

## Arquitectura
- **Frontend:** React (Pantalla inicial de Login y redireccionamientos OAuth).
- **Backend:** Laravel (`servicio-login`, controlador `AuthController`). Usa `Laravel Socialite` para la integración con Google.
- **Base de Datos:** MySQL (Tablas: `usuario_auth` para credenciales y tokens de sesión; relación con `usuario`).

---

## 1. Función: Inicio de Sesión Tradicional (Local)

### Descripción
El usuario ingresa su código o email y contraseña. El sistema verifica las credenciales, valida si la cuenta está activa y si pertenece al rol correspondiente al portal que intenta acceder (Académico o Administrativo), y retorna un token de sesión.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant AuthController
    participant Database

    Usuario->>Frontend: Ingresa credenciales (email y password)
    Frontend->>AuthController: POST /api/auth/login {codigoOEmail, password, tipoLogin}
    
    AuthController->>Database: Buscar usuario_auth por CorreoU o NumDoc
    
    alt Usuario NO existe o Inactivo
        Database-->>AuthController: null / inactivo
        AuthController-->>Frontend: HTTP 401/403 (Error de credenciales o cuenta)
        Frontend-->>Usuario: Muestra mensaje de error
    else Credenciales válidas
        Database-->>AuthController: auth + usuario_relacionado
        AuthController->>AuthController: Verifica base64_decode(password)
        AuthController->>Database: UPDATE usuario_auth (Genera SesionToken, ExpiraEn + 20min)
        AuthController-->>Frontend: HTTP 200 JSON { token, perfil }
        Frontend-->>Usuario: Redirige al Dashboard
    end
```

---

## 2. Función: Inicio de Sesión con Google (OAuth 2.0)

### Descripción
Permite a los usuarios acceder al sistema haciendo clic en "Iniciar sesión con Google". El backend redirige a los servidores de Google, y una vez aprobados, Google retorna los datos del usuario. Si el correo existe en nuestra base de datos, se genera la sesión.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant AuthController
    participant GoogleServer(OAuth)
    participant Database

    Usuario->>Frontend: Clic "Login con Google"
    Frontend->>AuthController: GET /api/auth/google/redirect
    AuthController-->>Usuario: Redirige a accounts.google.com
    
    Usuario->>GoogleServer(OAuth): Ingresa credenciales de Google
    GoogleServer(OAuth)-->>AuthController: GET /api/auth/google/callback (User Info)
    
    AuthController->>Database: Buscar usuario por email retornado
    
    alt No registrado
        Database-->>AuthController: null
        AuthController-->>Frontend: Redirige al Home con error (unauthorized)
    else Email Válido
        Database-->>AuthController: usuario_auth
        AuthController->>Database: UPDATE SesionToken y Expiración
        AuthController-->>Frontend: Redirige al Frontend con ?token=uuid
        Frontend->>Frontend: Guarda token y redirige a Dashboard
    end
```

---

## 3. Función: Validación de Sesión y Cierre de Sesión

### Descripción
El frontend invoca periódicamente `validateToken` para verificar si la sesión sigue viva y renovar el tiempo de inactividad (+20 min). También incluye la función `logout` explícita que anula el token.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor App(Frontend)
    participant AuthController
    participant Database

    %% Validación
    App(Frontend)->>AuthController: POST /api/auth/validate {token}
    AuthController->>Database: SELECT WHERE SesionToken = token
    
    alt Sesión Expirada
        Database-->>AuthController: ExpiraEn < Now
        AuthController->>Database: Limpia token
        AuthController-->>App(Frontend): HTTP 401 Unauthorized
    else Sesión Viva
        Database-->>AuthController: Data
        AuthController->>Database: Extiende ExpiraEn + 20 min
        AuthController-->>App(Frontend): HTTP 200 { perfil }
    end
    
    %% Logout
    App(Frontend)->>AuthController: POST /api/auth/logout {usuarioId}
    AuthController->>Database: Limpia SesionToken
    AuthController-->>App(Frontend): HTTP 204 No Content
```
