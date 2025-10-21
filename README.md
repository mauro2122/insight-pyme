# Insight PYME

Tablero simple para PYMEs: carga CSV (clientes, productos, ventas), muestra KPIs y estima demanda por producto.

- **Backend:** Flask + SQLAlchemy + SQLite  
- **ETL:** `python -m app.etl ...`  
- **Front:** HTML + JS + CSS  
- **Docs:** `/docs` (guía de usuario, guía técnica, plan de pruebas, bitácora)

## Demo local
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m app.etl --clientes data/clientes.csv --productos data/productos.csv --ventas data/ventas.csv --truncate true
python run.py
![Home](docs/img/home.png)
