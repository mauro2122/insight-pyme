
# Plan de Pruebas

## Funcionales
1. ETL con CSV válidos → DB con clientes, productos y ventas.
2. GET /api/kpis → retorna 200 y 3 KPIs.
3. GET /api/top-productos → ordenado desc y limitado por `limite`.
4. POST /api/demanda → responde con serie de puntos futuros.
5. UI `/`:
   - Carga lista de productos en <select>.
   - Muestra KPIs y Top productos.
   - Predicción grafica sin errores.

## No Funcionales
- Tiempo de respuesta < 1s en endpoints.
- Arranque de servidor sin errores.

## Evidencias (capturas)
- `docs/img/kpis.png`
- `docs/img/top_productos.png`
- `docs/img/prediccion.png`
- `docs/img/ventas.png`

### `docs/plan_pruebas.md`
```markdown
# Plan de pruebas – Insight PYME

## 1. Alcance
Verificar ETL, API y vistas.

## 2. Entorno
- Windows 10/11, Python 3.11
- Base SQLite
- Datos de ejemplo `data/*.csv`

## 3. Casos de prueba

### TP-01: ETL exitoso
**Pasos:** Ejecutar `python -m app.etl ... --truncate true`  
**Resultado esperado:** Mensaje "ETL terminado.", filas visibles en `app.db`.

### TP-02: KPIs con datos
**Pasos:** `python run.py` → abrir `/`  
**Esperado:** Clientes/Productos/Ventas con valores > 0.

### TP-03: Top productos
**Pasos:** `GET /api/top-productos?limite=3`  
**Esperado:** 3 registros ordenados por monto desc.

### TP-04: Predicción válida
**Pasos:** En la web seleccionar un producto con ventas, días=30, *Predecir*  
**Esperado:** JSON con `demanda_estimada` > 0.

### TP-05: Filtro de ventas por fecha
**Pasos:** `GET /api/ventas?desde=YYYY-MM-DD&hasta=YYYY-MM-DD`  
**Esperado:** ventas en rango; fuera de rango → vacío.

### TP-06: CSV inválido
**Pasos:** Ejecutar ETL con CSV sin columnas requeridas  
**Esperado:** Mensaje de error y no afecta la BD.

## 4. Evidencias
- Capturas en `docs/img/` y referencias en este documento.

## 5. Criterio de aceptación
Todos los casos TP-01 … TP-05 en verde y documentación actualizada.
