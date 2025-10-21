# app/etl.py
import csv
from datetime import datetime
import argparse

from app import create_app
from app.models import db, Cliente, Producto, Venta

def sniff_dialect(path):
    with open(path, 'rb') as fb:
        sample = fb.read(2048)
    # Intento con Sniffer; si falla, vuelvo a ','
    try:
        dialect = csv.Sniffer().sniff(sample.decode('utf-8', errors='ignore'))
        return dialect
    except Exception:
        class SimpleDialect(csv.Dialect):
            delimiter = ','
            quotechar = '"'
            doublequote = True
            skipinitialspace = True
            lineterminator = '\n'
            quoting = csv.QUOTE_MINIMAL
        return SimpleDialect()

def normalize_key(k: str) -> str:
    return (k or "").strip().lower()

def parse_fecha(value: str):
    v = (value or "").strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(v, fmt)
        except Exception:
            pass
    # último intento ISO
    try:
        return datetime.fromisoformat(v)
    except Exception:
        raise ValueError(f"Fecha inválida: {value!r}")

def read_rows(path):
    dialect = sniff_dialect(path)
    # utf-8-sig quita BOM si existe
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, dialect=dialect)
        if not reader.fieldnames:
            raise ValueError(f"{path}: no se detectaron cabeceras.")
        # normalizamos cabeceras
        field_map = {name: normalize_key(name) for name in reader.fieldnames}
        for row in reader:
            norm = {}
            for original_key, val in row.items():
                norm[field_map.get(original_key, original_key)] = (val or "").strip()
            yield norm

def cargar_clientes(path):
    for row in read_rows(path):
        # aceptamos variantes: id, cliente_id
        _id = row.get("id") or row.get("cliente_id")
        nombre = row.get("nombre")
        correo = row.get("correo") or row.get("email")
        if not _id:
            raise KeyError(f"{path}: falta columna 'id' (o 'cliente_id') en fila {row}")
        c = Cliente.query.get(int(_id))
        if not c:
            c = Cliente(id=int(_id))
        c.nombre = (nombre or "").strip()
        c.correo = (correo or "").strip() if correo else None
        db.session.add(c)
    db.session.commit()

def cargar_productos(path):
    for row in read_rows(path):
        _id = row.get("id") or row.get("producto_id")
        nombre = row.get("nombre")
        precio = row.get("precio") or row.get("valor") or row.get("price")
        if not _id:
            raise KeyError(f"{path}: falta 'id' (o 'producto_id') en fila {row}")
        p = Producto.query.get(int(_id))
        if not p:
            p = Producto(id=int(_id))
        p.nombre = (nombre or "").strip()
        p.precio = float(precio or 0)
        db.session.add(p)
    db.session.commit()

def cargar_ventas(path):
    for row in read_rows(path):
        _id = row.get("id")
        if not _id:
            raise KeyError(f"{path}: falta 'id' en fila {row}")
        v = Venta.query.get(int(_id))
        if not v:
            v = Venta(id=int(_id))
        v.fecha = parse_fecha(row.get("fecha"))
        # aceptar variantes
        v.cliente_id = int(row.get("cliente_id") or row.get("id_cliente") or 0) or None
        v.producto_id = int(row.get("producto_id") or row.get("id_producto") or 0) or None
        v.cantidad = int(row.get("cantidad") or row.get("qty") or 0)
        v.total = float(row.get("total") or row.get("monto") or 0)
        db.session.add(v)
    db.session.commit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clientes", required=True)
    parser.add_argument("--productos", required=True)
    parser.add_argument("--ventas", required=True)
    parser.add_argument("--truncate", default="false")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if str(args.truncate).lower() in ("true", "1", "yes", "y"):
            db.session.query(Venta).delete()
            db.session.query(Producto).delete()
            db.session.query(Cliente).delete()
            db.session.commit()

        cargar_clientes(args.clientes)
        cargar_productos(args.productos)
        cargar_ventas(args.ventas)

        print("Clientes:", Cliente.query.count())
        print("Productos:", Producto.query.count())
        print("Ventas:", Venta.query.count())
        print("ETL terminado.")

if __name__ == "__main__":
    main()
