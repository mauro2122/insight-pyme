
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
