# app/etl.py
import csv, argparse
from datetime import datetime
from dateutil import parser as dparser

from . import create_app
from .models import db, Cliente, Producto, Venta


def to_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return dparser.parse(s, dayfirst=False)

def load_clientes(path):
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            cli = Cliente(
                id=int(row.get("id") or 0),
                nombre=row.get("nombre") or "",
                email=row.get("email") or None,
            )
            db.session.merge(cli)
    db.session.commit()

def load_productos(path):
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            prod = Producto(
                id=int(row.get("id") or 0),
                nombre=row.get("nombre") or "",
                categoria=row.get("categoria") or None,
                precio=float(row.get("precio") or 0),
            )
            db.session.merge(prod)
    db.session.commit()

def load_ventas(path):
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            ven = Venta(
                id=int(row.get("id") or 0),
                cliente_id=int(row.get("cliente_id") or 0),
                producto_id=int(row.get("producto_id") or 0),
                fecha=to_date(row.get("fecha")),
                cantidad=int(row.get("cantidad") or 0),
                precio_unitario=float(row.get("precio_unitario") or 0),
                total=float(row.get("total") or 0),
            )
            db.session.merge(ven)
    db.session.commit()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--clientes")
    p.add_argument("--productos")
    p.add_argument("--ventas")
    p.add_argument("--truncate", default="false", help="true/false: vaciar tablas antes")
    args = p.parse_args()

    app = create_app()
    with app.app_context():
        if args.truncate.lower() == "true":
            Venta.query.delete()
            Producto.query.delete()
            Cliente.query.delete()
            db.session.commit()

        if args.clientes:  load_clientes(args.clientes)
        if args.productos: load_productos(args.productos)
        if args.ventas:    load_ventas(args.ventas)

        print("ETL terminado.")

if __name__ == "__main__":
    main()
