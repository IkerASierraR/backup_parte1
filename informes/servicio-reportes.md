# Servicio de Reportes (servicio-reportes)

## Descripción
Este microservicio administrativo tiene el propósito de consolidar la información del sistema de reservas para extraer métricas y estadísticas relevantes de uso institucional. Provee al dashboard del administrador datos consolidados (KPIs) y permite exportar dichos resultados en formatos de reporte estándar (PDF y Excel).

## Arquitectura
- **Frontend:** React (Sección "Dashboard / Reportes" del panel de administración).
- **Backend:** Laravel (`servicio-reportes`, controlador `ReportesController`). Usa librerías como `barryvdh/laravel-dompdf` para PDF y `maatwebsite/excel` para Excel.
- **Base de Datos:** MySQL (Consulta intensiva sobre tablas de `reserva`, `espacio`, etc., mediante queries agregadas `GROUP BY`).

---

## 1. Función: Dashboards Estadísticos (APIs JSON)

### Descripción
Provee información estructurada para renderizar los gráficos de la interfaz (ej. Gráficos de barra, pie o líneas). Obtiene KPIs generales, top espacios más usados y la curva de crecimiento de reservas por mes.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant ReportesController
    participant ReportesService
    participant Database

    Admin->>Frontend: Carga la pantalla "Reportes"
    
    par Consultas Paralelas
        Frontend->>ReportesController: GET /api/reportes/estadisticas-generales
        ReportesController->>ReportesService: obtenerEstadisticasGenerales()
        ReportesService->>Database: COUNT(reservas), aprobadas vs rechazadas
        Database-->>ReportesService: KPIs
        ReportesService-->>ReportesController: Array
        ReportesController-->>Frontend: HTTP 200 JSON
        
        Frontend->>ReportesController: GET /api/reportes/uso-espacios
        ReportesController->>ReportesService: obtenerUsoEspacios()
        ReportesService->>Database: GROUP BY espacio ORDER BY count DESC LIMIT 10
        Database-->>ReportesService: Top Espacios
        ReportesService-->>ReportesController: Array
        ReportesController-->>Frontend: HTTP 200 JSON
        
        Frontend->>ReportesController: GET /api/reportes/reservas-mes
        ReportesController->>ReportesService: obtenerReservasPorMes()
        ReportesService->>Database: GROUP BY mes
        Database-->>ReportesService: Tendencias
        ReportesService-->>ReportesController: Array
        ReportesController-->>Frontend: HTTP 200 JSON
    end
    
    Frontend-->>Admin: Renderiza gráficos de barras y torta
```

---

## 2. Función: Exportación Documental (PDF y Excel)

### Descripción
Permite a la gerencia descargar un reporte formal (imprimible o calculable) con toda la consolidación estadística generada por el sistema.

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Admin
    participant Frontend
    participant ReportesController
    participant ReportesService
    participant LibreriaExport
    participant Database

    Admin->>Frontend: Clic en "Exportar a PDF"
    Frontend->>ReportesController: GET /api/reportes/exportacion/pdf
    
    ReportesController->>ReportesService: Obtiene toda la metadata (Generales, Espacios, Mensual)
    ReportesService->>Database: Multiples consultas
    Database-->>ReportesService: Data Completa
    
    ReportesController->>LibreriaExport: Carga Data en Vista HTML (reports.pdf)
    LibreriaExport->>LibreriaExport: Renderiza HTML a PDF
    LibreriaExport-->>ReportesController: Archivo Binario (.pdf)
    
    ReportesController-->>Frontend: HTTP 200 (application/pdf) File Download
    Frontend-->>Admin: Descarga "reporte_estadisticas_20261102_1500.pdf"
```
