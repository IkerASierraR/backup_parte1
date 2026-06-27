# Servicio de Cafetería (servicio-cafeteria)

## Descripción
Este microservicio administra la red de cafeterías dentro del campus. Gestiona la información de los locales, su inventario (productos) y el flujo completo de pedidos realizados por los usuarios (estudiantes/docentes). Incluye la validación de pagos, cambios de estado del pedido (pendiente, preparando, listo, entregado) y confirmación de recojo mediante código QR.

## Arquitectura
- **Frontend:** React (Llamadas Axios a los endpoints expuestos).
- **Backend:** Laravel (`servicio-cafeteria` con controladores dedicados: `CafeteriaController`, `ProductoController`, `PedidoController`).
- **Base de Datos:** MySQL (Tablas principales: `cafeterias`, `cafeteria_productos`, `cafeteria_pedidos`, `cafeteria_pedido_items`).

---

## 1. Función: Gestión de Cafeterías

### Descripción
Permite a un administrador del sistema listar, registrar y actualizar las concesiones de cafeterías, así como habilitar o deshabilitar su funcionamiento (`cambiarEstado`).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant CafeteriaController
    participant CafeteriaService
    participant Database

    Admin->>Frontend: Registra nueva cafetería
    Frontend->>CafeteriaController: POST /api/cafeterias {nombre, ubicacion...}
    
    CafeteriaController->>CafeteriaService: crear(datos)
    CafeteriaService->>Database: INSERT INTO cafeterias...
    Database-->>CafeteriaService: Cafetería creada
    
    CafeteriaService-->>CafeteriaController: Cafeteria (Model)
    CafeteriaController->>CafeteriaController: mapear(cafeteria)
    CafeteriaController-->>Frontend: HTTP 201 JSON
```

---

## 2. Función: Gestión de Productos (Menú)

### Descripción
Permite al concesionario de una cafetería específica registrar los productos que ofrece (almuerzos, snacks, bebidas), establecer sus precios, stock y disponibilidad.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Concesionario
    participant Frontend
    participant ProductoController
    participant ProductoService
    participant Database

    Concesionario->>Frontend: Agrega producto al menú
    Frontend->>ProductoController: POST /api/cafeterias/{id}/productos {nombre, precio...}
    
    ProductoController->>ProductoController: Valida request (ProductoRequest)
    
    ProductoController->>ProductoService: crear(IdCafeteria, datos...)
    ProductoService->>Database: INSERT INTO cafeteria_productos...
    Database-->>ProductoService: Producto creado
    
    ProductoService-->>ProductoController: CafeteriaProducto
    ProductoController-->>Frontend: HTTP 201 JSON
```

---

## 3. Función: Realizar y Gestionar Pedidos

### Descripción
Es el flujo core. Un usuario hace un pedido, adjuntando su comprobante de pago. El concesionario aprueba el pago, pasa a prepararlo, notifica que está listo, y finalmente el usuario lo recoge mostrando un QR que el concesionario escanea (checkin).

### Diagrama Mermaid (Creación y Aprobación)

```mermaid
sequenceDiagram
    actor Usuario
    actor Concesionario
    participant Frontend
    participant PedidoController
    participant PedidoService
    participant Database

    %% Creación del Pedido
    Usuario->>Frontend: Confirma carrito y sube voucher
    Frontend->>PedidoController: POST /api/cafeterias/{id}/pedidos (Multipart)
    
    PedidoController->>PedidoController: Guarda archivo de comprobante
    PedidoController->>PedidoService: crear(usuarioId, items, comprobanteUrl...)
    PedidoService->>Database: DB::transaction -> INSERT pedido & items
    Database-->>PedidoService: OK (Estado: pendiente_confirmacion)
    PedidoService-->>PedidoController: Pedido
    PedidoController-->>Frontend: HTTP 201 JSON
    
    %% Aprobación del Pedido
    Concesionario->>Frontend: Verifica voucher y aprueba
    Frontend->>PedidoController: PATCH /api/pedidos/{idPedido}/aprobar
    
    PedidoController->>PedidoService: aprobar(idPedido)
    PedidoService->>Database: UPDATE estado = 'preparando'
    Database-->>PedidoService: OK
    PedidoService-->>PedidoController: Pedido actualizado
    PedidoController-->>Frontend: HTTP 200 JSON
```

---

## 4. Función: Check-in de Pedido (Código QR)

### Descripción
Cuando el usuario llega a recoger su pedido, el concesionario escanea un código QR generado por la App, lo que valida la entrega y pasa el pedido al estado final `entregado`.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Concesionario
    participant Frontend
    participant PedidoController
    participant PedidoService
    participant Database

    Concesionario->>Frontend: Escanea QR del alumno
    Frontend->>PedidoController: POST /api/pedidos/checkin {codigoQr}
    
    PedidoController->>PedidoService: checkin(codigoQr)
    PedidoService->>Database: SELECT * FROM cafeteria_pedidos WHERE CodigoQr = ?
    Database-->>PedidoService: Pedido
    
    alt Pedido no es válido o no está listo
        PedidoService-->>PedidoController: throw RuntimeException / InvalidArgumentException
        PedidoController-->>Frontend: HTTP 422 Unprocessable Entity
    else Pedido Listo
        PedidoService->>Database: UPDATE estado = 'entregado', fechaEntrega = NOW()
        Database-->>PedidoService: OK
        PedidoService-->>PedidoController: Pedido actualizado
        PedidoController-->>Frontend: HTTP 200 JSON (Entrega exitosa)
    end
```
