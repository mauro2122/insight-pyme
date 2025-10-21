# Insight-PYME

Aplicación Flask para analítica de ventas en PYMES: carga CSV (ETL), API de KPIs y predicción de demanda, y una página web simple para consulta.

## 📦 Stack
- Python 3.11+ (ok 3.13)
- Flask + SQLAlchemy + SQLite
- HTML/CSS/JS vanilla

## 🚀 Cómo ejecutar
```bash
# 1) crear y activar venv (si no existe)
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# 2) instalar dependencias
pip install -r requirements.txt

# 3) cargar datos iniciales
python -m app.etl --clientes data/clientes.csv --productos data/productos.csv --ventas data/ventas.csv --truncate true

# 4) levantar servidor (ver puerto en consola)
python run.py
