# Guía de Usuario – Insight-PYME

## 1. Preparación
- Activar entorno: `.venv\Scripts\Activate.ps1`
- Ejecutar ETL: `python -m app.etl --clientes data/clientes.csv --productos data/productos.csv --ventas data/ventas.csv --truncate true`

## 2. Abrir la app
- `python run.py` → abrir la URL que aparece (ej. http://127.0.0.1:5000/)

## 3. Funciones
- **KPIs**: tarjetas con total de clientes, productos y ventas.
- **Top productos**: tabla dinámica con monto vendido.
- **Predicción de demanda**: seleccionar un producto y un rango de días, luego “Predecir”.
- **Ventas**: listado de ventas recientes con filtros por fecha.

## 4. Errores comunes
- “No hay datos”: Ejecuta el ETL.
- “500 interno”: Ver consola; casi siempre es ruta o CSV con formato distinto.
