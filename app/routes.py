# app/routes.py
from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from .models import db, Cliente, Producto, Venta
from .analytics import AnalyticsEngine

main = Blueprint("main", __name__)

# --------- PÁGINA ----------
@main.get("/")
def home():
    # Carga productos para el <select> del template
    productos = db.session.query(Producto).order_by(Producto.id.asc()).all()
    return render_template("home.html", productos=productos)

# (opcional) healthcheck en JSON
@main.get("/api/health")
def health():
    return jsonify({"ok": True, "msg": "API Insight-PYME"})

# --------- APIS ----------
@main.get("/api/kpis")
def kpis():
    total_clientes = Cliente.query.count()
    total_productos = Producto.query.count()
    total_ventas = db.session.query(db.func.coalesce(db.func.sum(Venta.total), 0)).scalar() or 0
    return jsonify({
        "clientes": total_clientes,
        "productos": total_productos,
        "ventas_total": float(total_ventas),
    })

@main.get("/api/top-productos")
def top_productos():
    limite = int(request.args.get("limite", 5))
    rows = (
        db.session.query(Producto.id, Producto.nombre, db.func.sum(Venta.total).label("monto"))
        .join(Venta, Venta.producto_id == Producto.id)
        .group_by(Producto.id, Producto.nombre)
        .order_by(db.desc("monto"))
        .limit(limite)
        .all()
    )
    data = [{"producto_id": r.id, "nombre": r.nombre, "monto": float(r.monto)} for r in rows]
    return jsonify(data)

# POST que usa el frontend (JS) para predecir
@main.post("/api/demanda")
def api_demanda():
    data = request.get_json(silent=True) or {}
    producto_id = int(data.get("producto_id", 0))
    dias = int(data.get("dias_futuro", 30))
    res = AnalyticsEngine.predecir_demanda(producto_id, dias_futuro=dias)
    return jsonify(res)

# (opcional) versión GET para probar por URL
@main.get("/api/demanda/<int:producto_id>")
def demanda_get(producto_id):
    dias = int(request.args.get("dias", 30))
    res = AnalyticsEngine.predecir_demanda(producto_id, dias_futuro=dias)
    return jsonify(res)

@main.get("/api/ventas")
def listar_ventas():
    """?desde=YYYY-MM-DD&hasta=YYYY-MM-DD (opcional)"""
    q = Venta.query
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    if desde:
        q = q.filter(Venta.fecha >= datetime.fromisoformat(desde))
    if hasta:
        q = q.filter(Venta.fecha <= datetime.fromisoformat(hasta))
    q = q.order_by(Venta.fecha.desc()).limit(100)
    data = [{
        "id": v.id,
        "fecha": v.fecha.isoformat(),
        "cliente": v.cliente.nombre if v.cliente else None,
        "producto": v.producto.nombre if v.producto else None,
        "cantidad": v.cantidad,
        "total": float(v.total),
    } for v in q.all()]
    return jsonify(data)
@main.get("/api/ventas-por-hora")
def api_ventas_por_hora():
    return jsonify(AnalyticsEngine.get_ventas_por_hora())

@main.get("/api/ventas-por-dia")
def api_ventas_por_dia():
    return jsonify(AnalyticsEngine.get_ventas_por_dia_semana())
