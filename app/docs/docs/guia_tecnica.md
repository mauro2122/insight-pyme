# Guía Técnica – Insight-PYME

## Requisitos
- Python 3.11+ (funciona con 3.13)
- Windows PowerShell o CMD

## Instalación
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt


# Guía técnica – Insight PYME

## 1. Arquitectura
- **Flask** (API + vistas): `app/__init__.py`, `app/routes.py`
- **ORM (SQLAlchemy)**: `app/models.py`
- **ETL local**: `app/etl.py`
- **Front**: `app/templates/*.html`, `app/static/{app.js,style.css}`
- **DB**: SQLite (`app.db`, configurable)

## 2. Configuración
`app/config.py`:
- cadena de conexión SQLite por defecto.
- debug=True en desarrollo.

## 3. Modelos
- `Cliente(id, nombre, ciudad)`
- `Producto(id, nombre, categoria, precio)`
- `Venta(id, fecha, cliente_id, producto_id, cantidad, total)`

## 4. Endpoints principales
- `GET /` → template `home.html`
- `GET /api/kpis` → {clientes, productos, ventas_total}
- `GET /api/top-productos?limite=5`
- `POST /api/demanda` → body `{producto_id, dias_futuro}`
- `GET /api/ventas?desde&hasta`

## 5. ETL
- Limpia tablas si `--truncate true`
- Carga CSV → valida → inserta en bloque
- Manejo de errores básico y logs por consola

## 6. Predicción (baseline)
`AnalyticsEngine.predecir_demanda()`:
- Promedio diario simple de ventas históricas del producto
- Proyección = promedio * días_futuro
- Retorna `{demanda_estimada, promedio_diario, horizonte_dias}`

## 7. Ejecución
```bash
.venv\Scripts\activate
python run.py
