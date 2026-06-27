# Servicio de Auditoría (servicio-auditoria)

## Descripción
Este microservicio se encarga de rastrear y proporcionar el historial de cambios, gestiones y estados de las reservas de la plataforma. Permite visualizar qué usuario realizó una acción, cuándo la hizo y exportar estos reportes a formatos PDF y Excel.

## Arquitectura
- **Frontend:** React (Llamadas HTTP a la API de auditorías para poblar tablas y descargar reportes).
- **Backend:** Laravel (Expone endpoints REST en `AuditoriaController`, con la lógica encapsulada en `AuditoriaService` y `AuditoriaExportService`).
- **Base de Datos:** MySQL (Probablemente consulta las tablas de log como `reserva_gestion` y `reserva`).

---

## 1. Función: Listar y Filtrar Auditorías

### Descripción
Recupera el historial de auditoría basado en filtros como el ID de la reserva, estado, usuario y un rango de fechas.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant AuditoriaController
    participant AuditoriaService
    participant Database

    Admin->>Frontend: Filtra historial de auditoría
    Frontend->>AuditoriaController: GET /api/auditorias?reservaId=...&fechaInicio=...
    
    AuditoriaController->>AuditoriaController: construirFiltro(request)
    AuditoriaController->>AuditoriaController: parseFecha(fechaInicio, fechaFin)
    
    AuditoriaController->>AuditoriaService: buscar(filtro)
    AuditoriaService->>Database: SELECT * FROM reserva_gestion WHERE filtros...
    Database-->>AuditoriaService: Resultados de auditoría
    
    AuditoriaService-->>AuditoriaController: Lista de auditorías
    AuditoriaController-->>Frontend: HTTP 200 JSON
    Frontend-->>Admin: Muestra resultados en tabla
```

---

## 2. Función: Detalle de Auditoría e Historial por Reserva

### Descripción
Obtiene el detalle específico de un registro de auditoría (`/auditorias/{id}`) o el historial completo de gestiones para una reserva específica (`/auditorias/reserva/{reservaId}`).

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend
    participant AuditoriaController
    participant AuditoriaService
    participant Database

    Usuario->>Frontend: Selecciona Ver Historial de Reserva
    Frontend->>AuditoriaController: GET /api/auditorias/reserva/{reservaId}
    
    AuditoriaController->>AuditoriaController: Valida reservaId > 0
    
    AuditoriaController->>AuditoriaService: listarPorReserva(reservaId)
    AuditoriaService->>Database: SELECT * FROM reserva_gestion WHERE reservaId = ? ORDER BY fecha
    Database-->>AuditoriaService: Historial de la reserva
    
    AuditoriaService-->>AuditoriaController: Data del historial
    AuditoriaController-->>Frontend: HTTP 200 JSON
    Frontend-->>Usuario: Despliega modal o timeline
```

---

## 3. Función: Exportar Auditoría (PDF / Excel)

### Descripción
Genera un archivo binario descargable (PDF o Excel) con los registros de auditoría aplicando los filtros seleccionados por el usuario.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant AuditoriaController
    participant AuditoriaExportService
    participant Database
    participant GeneradorArchivos (DomPDF / PhpSpreadsheet)

    Admin->>Frontend: Clic en "Exportar PDF" o "Excel"
    Frontend->>AuditoriaController: GET /api/auditorias/exportacion/pdf (o excel)
    
    AuditoriaController->>AuditoriaController: construirFiltro(request)
    
    alt Es PDF
        AuditoriaController->>AuditoriaExportService: generarPdf(filtro)
    else Es Excel
        AuditoriaController->>AuditoriaExportService: generarExcel(filtro)
    end
    
    AuditoriaExportService->>Database: SELECT * FROM reserva_gestion WHERE filtros...
    Database-->>AuditoriaExportService: Datos crudos
    
    AuditoriaExportService->>GeneradorArchivos: Formatea y renderiza (PDF/XLSX)
    GeneradorArchivos-->>AuditoriaExportService: Archivo binario generado
    
    AuditoriaExportService-->>AuditoriaController: binary data
    
    AuditoriaController-->>Frontend: HTTP 200 con Content-Disposition: attachment
    Frontend-->>Admin: Descarga automática de reporte_auditoria_xxx.pdf/xlsx
```
