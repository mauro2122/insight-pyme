# app/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = "clientes"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)

    ventas = db.relationship("Venta", backref="cliente", lazy=True)

class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    categoria = db.Column(db.String(80), nullable=True)
    precio = db.Column(db.Float, default=0.0)

    ventas = db.relationship("Venta", backref="producto", lazy=True)

class Venta(db.Model):
    __tablename__ = "ventas"
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    cantidad = db.Column(db.Integer, default=0)
    precio_unitario = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
