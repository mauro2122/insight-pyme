# app/routes.py
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import func

from .models import db, Cliente, Producto, Venta
from .analytics import AnalyticsEngine

main = Blueprint("main", __name__)


# ----------------------------
# Helpers locales (fechas)
# ----------------------------
def _parse_date(s: str | None):
    """Convierte 'YYYY-MM-DD' a datetime 00:00, o None si viene vacío o mal."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _end_of_day(dt):
    """Devuelve dt + 1 día (para usar como límite exclusivo '<')."""
    return dt + timedelta(days=1) if dt else None


# ----------------------------
# PÁGINA
# ----------------------------
@main.get("/")
def home():
    # Productos para el <select>
    productos = db.session.query(Producto).order_by(Producto.nombre.asc()).all()

    # Rango de fechas disponible en la BD (opcional para el template)
    minmax = db.session.query(func.min(Venta.fecha), func.max(Venta.fecha)).first()
    min_fecha = minmax[0].date().isoformat() if minmax and minmax[0] else None
    max_fecha = minmax[1].date().isoformat() if minmax and minmax[1] else None

    return render_template(
        "home.html",
        productos=productos,
        min_fecha=min_fecha,
        max_fecha=max_fecha,
    )


# (opcional) healthcheck en JSON
@main.get("/api/health")
def health():
    return jsonify({"ok": True, "msg": "API Insight-PYME"})


# ----------------------------
# APIS DE NEGOCIO
# ----------------------------
@main.get("/api/kpis")
def api_kpis():
    """
    KPIs con rango opcional:
      GET /api/kpis?desde=YYYY-MM-DD&hasta=YYYY-MM-DD
    Si no se envía rango, usa el comportamiento original (mes actual vs anterior).
    """
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    data = AnalyticsEngine.get_kpis(desde=desde, hasta=hasta)
    return jsonify(data)


@main.get("/api/top-productos")
def api_top_productos():
    """
    Top productos con rango opcional:
      GET /api/top-productos?limite=5&desde=YYYY-MM-DD&hasta=YYYY-MM-DD
    """
    limite = int(request.args.get("limite", 5))
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")

    data = AnalyticsEngine.get_top_productos(
        limite=limite, desde=desde, hasta=hasta
    )
    # Estructura: [{"producto": "...", "cantidad": N, "ingreso": 123.45}, ...]
    return jsonify(data)


# Predicción (POST que usa el frontend)
@main.post("/api/demanda")
def api_demanda():
    data = request.get_json(silent=True) or {}
    producto_id = int(data.get("producto_id", 0))
    dias = int(data.get("dias_futuro", 30))

    if not producto_id:
        return jsonify({"error": "producto_id requerido"}), 400

    res = AnalyticsEngine.predecir_demanda(producto_id, dias_futuro=dias)
    return jsonify(res)


# (opcional) versión GET de la predicción (para pruebas rápidas por URL)
@main.get("/api/demanda/<int:producto_id>")
def api_demanda_get(producto_id):
    dias = int(request.args.get("dias", 30))
    res = AnalyticsEngine.predecir_demanda(producto_id, dias_futuro=dias)
    return jsonify(res)


@main.get("/api/ventas")
def api_listar_ventas():
    """
    Listado simple (máx 1000) con filtro opcional por fecha (INCLUSIVO):
      GET /api/ventas?desde=YYYY-MM-DD&hasta=YYYY-MM-DD
    """
    q = db.session.query(Venta).order_by(Venta.fecha.desc())

    d = _parse_date(request.args.get("desde"))
    h = _parse_date(request.args.get("hasta"))
    if d:
        q = q.filter(Venta.fecha >= d)
    if h:
        q = q.filter(Venta.fecha < _end_of_day(h))

    q = q.limit(1000)
    data = [{
        "id": v.id,
        "fecha": v.fecha.isoformat(),
        "cliente": v.cliente.nombre if v.cliente else None,
        "producto": v.producto.nombre if v.producto else None,
        "cantidad": int(v.cantidad or 0),
        "total": float(v.total or 0.0),
    } for v in q.all()]
    return jsonify(data)


@main.get("/api/ventas-por-hora")
def api_ventas_por_hora():
    """
    Barras por hora con rango opcional:
      GET /api/ventas-por-hora?desde=YYYY-MM-DD&hasta=YYYY-MM-DD
    """
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    data = AnalyticsEngine.get_ventas_por_hora(desde=desde, hasta=hasta)
    return jsonify(data)


@main.get("/api/ventas-por-dia")
def api_ventas_por_dia():
    """
    Barras por día de la semana con rango opcional:
      GET /api/ventas-por-dia?desde=YYYY-MM-DD&hasta=YYYY-MM-DD
    """
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    data = AnalyticsEngine.get_ventas_por_dia_semana(desde=desde, hasta=hasta)
    return jsonify(data)


# ----------------------------
# APIS DE APOYO PARA EL FRONT
# ----------------------------
@main.get("/api/productos")
def api_productos():
    """Lista simple de productos para poblar selects en el front."""
    prods = db.session.query(Producto.id, Producto.nombre).order_by(Producto.nombre.asc()).all()
    return jsonify([{"id": p.id, "nombre": p.nombre} for p in prods])


@main.get("/api/rango-fechas")
def api_rango_fechas():
    """
    Devuelve la fecha mínima y máxima existentes en ventas,
    útil para inicializar datepickers en el front.
    """
    row = db.session.query(func.min(Venta.fecha), func.max(Venta.fecha)).first()
    return jsonify({
        "min": row[0].date().isoformat() if row and row[0] else None,
        "max": row[1].date().isoformat() if row and row[1] else None,
    })
