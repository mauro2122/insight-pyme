# app/analytics.py
from datetime import datetime, timedelta
from sqlalchemy import func
import math

from .models import db, Venta, Producto, Cliente

class AnalyticsEngine:
    """Motor de análisis de datos para Insight PYME"""

    # ---- KPIs PRINCIPALES ----
    @staticmethod
    def get_kpis():
        hoy = datetime.now()
        inicio_mes = hoy.replace(day=1)
        mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)

        ventas_mes = db.session.query(func.sum(Venta.total)) \
            .filter(Venta.fecha >= inicio_mes).scalar() or 0.0

        ventas_mes_anterior = db.session.query(func.sum(Venta.total)) \
            .filter(Venta.fecha >= mes_anterior, Venta.fecha < inicio_mes).scalar() or 0.0

        crecimiento = ((ventas_mes - ventas_mes_anterior) / ventas_mes_anterior * 100.0) \
            if ventas_mes_anterior > 0 else 0.0

        ticket_promedio = db.session.query(func.avg(Venta.total)) \
            .filter(Venta.fecha >= inicio_mes).scalar() or 0.0

        productos_vendidos = db.session.query(func.sum(Venta.cantidad)) \
            .filter(Venta.fecha >= inicio_mes).scalar() or 0

        clientes_unicos = db.session.query(func.count(func.distinct(Venta.cliente_id))) \
            .filter(Venta.fecha >= inicio_mes, Venta.cliente_id.isnot(None)).scalar() or 0

        return {
            "ventas_mes": float(round(ventas_mes, 2)),
            "crecimiento": float(round(crecimiento, 2)),
            "ticket_promedio": float(round(ticket_promedio, 2)),
            "productos_vendidos": int(productos_vendidos),
            "clientes_unicos": int(clientes_unicos),
        }

    # ---- TOP PRODUCTOS ----
    @staticmethod
    def get_top_productos(limite=10):
        filas = (
            db.session.query(
                Producto.nombre,
                Producto.categoria,
                func.sum(Venta.cantidad).label("cant"),
                func.sum(Venta.total).label("ing"),
            )
            .join(Venta, Venta.producto_id == Producto.id)
            .group_by(Producto.id)
            .order_by(func.sum(Venta.total).desc())
            .limit(limite)
            .all()
        )
        return [
            {
                "producto": f[0],
                "categoria": f[1],
                "cantidad": int(f[2] or 0),
                "ingreso": float(round(f[3] or 0.0, 2)),
            }
            for f in filas
        ]

    # ---- VENTAS POR HORA ----
    @staticmethod
    def get_ventas_por_hora():
        totales = {h: 0.0 for h in range(24)}
        for v in Venta.query.all():
            totales[v.fecha.hour] += float(v.total or 0.0)
        return [{"hora": f"{h:02d}:00", "ventas": float(round(totales[h], 2))} for h in range(24)]

    # ---- VENTAS POR DÍA DE LA SEMANA ----
    @staticmethod
    def get_ventas_por_dia_semana():
        nombres = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        totales = {i: 0.0 for i in range(7)}
        for v in Venta.query.all():
            totales[v.fecha.weekday()] += float(v.total or 0.0)
        return [{"dia": nombres[i], "ventas": float(round(totales[i], 2))} for i in range(7)]

    # ---- SEGMENTACIÓN (RFM simple) ----
    @staticmethod
    def segmentar_clientes():
        datos = (
            db.session.query(
                Cliente.id,
                Cliente.nombre,
                func.max(Venta.fecha).label("ultima"),
                func.count(Venta.id).label("freq"),
                func.sum(Venta.total).label("mont"),
            )
            .join(Venta, Venta.cliente_id == Cliente.id)
            .group_by(Cliente.id)
            .all()
        )
        if not datos:
            return []

        # Stats para percentiles
        freqs = [d[3] or 0 for d in datos]
        montos = [float(d[4] or 0.0) for d in datos]
        p50_freq = sorted(freqs)[len(freqs) // 2]
        p75_monto = sorted(montos)[int(len(montos) * 0.75)]

        res = []
        for d in datos:
            recencia = (datetime.now() - d[2]).days if d[2] else 9999
            freq = int(d[3] or 0)
            monto = float(d[4] or 0.0)

            if monto > p75_monto and freq > p50_freq:
                segmento = "VIP"
            elif recencia > 90:
                segmento = "En Riesgo"
            elif freq > p50_freq:
                segmento = "Regular"
            else:
                segmento = "Ocasional"

            # guardar en DB (opcional)
            cli = Cliente.query.get(d[0])
            if cli:
                cli.segmento = segmento

            res.append({
                "cliente_id": d[0],
                "nombre": d[1],
                "recencia": recencia,
                "frecuencia": freq,
                "monto": float(round(monto, 2)),
                "segmento": segmento,
            })

        db.session.commit()
        return res

    # ---- CLV ESTIMADO ----
    @staticmethod
    def calcular_clv(cliente_id):
        compras = Venta.query.filter_by(cliente_id=cliente_id).order_by(Venta.fecha).all()
        if not compras:
            return 0.0

        total = sum(float(c.total or 0.0) for c in compras)
        n = len(compras)
        valor_promedio = total / n

        if n > 1:
            dias = (compras[-1].fecha - compras[0].fecha).days or 1
            freq_dias = dias / (n - 1)
        else:
            freq_dias = 30.0

        compras_por_anio = 365.0 / freq_dias
        clv = valor_promedio * compras_por_anio * 2  # horizonte 2 años
        return float(round(clv, 2))

    # ---- PREDICCIÓN DE DEMANDA (promedio simple) ----
    @staticmethod
    def predecir_demanda(producto_id, dias_futuro=30):
        ventas = (
            db.session.query(Venta)
            .filter(Venta.producto_id == producto_id)
            .order_by(Venta.fecha.asc())
            .all()
        )
        # UMBRAL BAJO PARA DEMO
        if len(ventas) < 1:
            print("DEBUG analytics: sin ventas para producto", producto_id)  # <— LOG
            return {"error": "Datos insuficientes"}

        # agregamos por día
        por_dia = {}
        for v in ventas:
            clave = v.fecha.date()
            por_dia[clave] = por_dia.get(clave, 0) + int(v.cantidad or 0)

        if not por_dia:
            return {"error": "Datos insuficientes"}

        promedio_diario = sum(por_dia.values()) / len(por_dia)
        demanda = promedio_diario * dias_futuro

        return {
            "demanda_estimada": int(round(demanda)),
            "promedio_diario": float(round(promedio_diario, 2)),
            "horizonte_dias": dias_futuro,
        }
