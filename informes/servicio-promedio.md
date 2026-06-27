# Servicio de Calculadora de Promedios (servicio-promedio)

## Descripción
Este es un microservicio utilitario y sin estado (stateless) diseñado para ayudar a los estudiantes a proyectar sus calificaciones. Basado en las notas obtenidas y el peso porcentual de cada unidad académica, calcula cuánto necesita sacar el estudiante en las siguientes evaluaciones para aprobar el curso (la nota aprobatoria es 10.5).

## Arquitectura
- **Frontend:** React (Calculadora interactiva donde el estudiante ingresa las notas que ya tiene y los porcentajes).
- **Backend:** Laravel (`servicio-promedio`, controlador único `PromedioController`). No requiere conexión a base de datos.
- **Base de Datos:** N/A (Es una API de cálculo matemático puro en memoria).

---

## 1. Función: Calcular Promedio Proyectado

### Descripción
Recibe un arreglo de unidades (cada una con su `nota` obtenida y su `porcentaje` respectivo). Suma lo acumulado y calcula, sobre el porcentaje faltante, la nota exacta que el alumno necesita en las próximas evaluaciones para llegar a 10.5. También devuelve mensajes personalizados (ej. "Tan cerca y a la vez tan lejos", "Al otro año será").

### Diagrama Mermaid

```mermaid
sequenceDiagram
    actor Estudiante
    participant Frontend
    participant PromedioController

    Estudiante->>Frontend: Ingresa Unidad 1 (Nota: 08, 30%) y Unidad 2 (Sin nota, 70%)
    Frontend->>PromedioController: POST /api/promedio/calcular {unidades: [...]}
    
    PromedioController->>PromedioController: Calcula nota acumulada = (08 * 0.3) = 2.4
    PromedioController->>PromedioController: Calcula porcentaje faltante = 70%
    
    PromedioController->>PromedioController: Meta = 10.5. Necesita = (10.5 - 2.4) / 0.7 = 11.57
    PromedioController->>PromedioController: Valida si es posible (nota <= 20)
    
    PromedioController->>PromedioController: Asigna mensaje personalizado de acuerdo a los rangos
    
    PromedioController-->>Frontend: HTTP 200 JSON {acumulado, notaNecesaria, posible, mensaje}
    Frontend-->>Estudiante: Muestra: "Necesitas sacar 11.57 en el restante 70%"
```
