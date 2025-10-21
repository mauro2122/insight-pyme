// app/static/app.js
document.addEventListener("DOMContentLoaded", () => {
  // Estado de filtros
  const state = { desde: null, hasta: null };

  // Formateadores
  const fmtMoney   = v => `$ ${Number(v ?? 0).toLocaleString("es-CO", { maximumFractionDigits: 0 })}`;
  const fmtPercent = v => `${Number(v ?? 0).toFixed(1)}%`;

  // Elementos
  const fDesde = document.getElementById("f-desde");
  const fHasta = document.getElementById("f-hasta");
  document.getElementById("btn-aplicar").addEventListener("click", () => {
    state.desde = fDesde.value || null;
    state.hasta = fHasta.value || null;
    refreshAll();
  });
  document.getElementById("btn-limpiar").addEventListener("click", () => {
    fDesde.value = ""; fHasta.value = "";
    state.desde = state.hasta = null;
    refreshAll();
  });

  // Predicción
  prepararFormulario();

  // Gráficos: manejamos referencias para destruir/recrear
  let chartHora = null, chartDia = null;

  function qs() {
    const p = new URLSearchParams();
    if (state.desde) p.set("desde", state.desde);
    if (state.hasta) p.set("hasta", state.hasta);
    const s = p.toString();
    return s ? `?${s}` : "";
  }

  async function pintarKPIs() {
    try {
      const r = await fetch(`/api/kpis${qs()}`);
      const k = await r.json();
      document.getElementById("kpi-ventas-mes").textContent = fmtMoney(k.ventas_mes);
      document.getElementById("kpi-crecimiento").textContent = fmtPercent(k.crecimiento);
      document.getElementById("kpi-ticket").textContent = fmtMoney(k.ticket_promedio);
      document.getElementById("kpi-clientes").textContent = Number(k.clientes_unicos ?? 0).toLocaleString("es-CO");
    } catch (e) {
      console.error(e);
    }
  }

  async function pintarTopProductos() {
    const body = document.getElementById("top-body");
    body.innerHTML = `<tr><td colspan="2" class="text-center text-secondary">Cargando…</td></tr>`;
    try {
      const r = await fetch(`/api/top-productos${qs()}&limite=10`);
      const arr = await r.json();
      if (!arr.length) {
        body.innerHTML = `<tr><td colspan="2" class="text-center text-secondary">Sin datos</td></tr>`;
        return;
      }
      body.innerHTML = arr.map(x =>
        `<tr><td>${x.producto || x.nombre}</td><td class="text-end">${fmtMoney(x.monto || x.ingreso || 0)}</td></tr>`
      ).join("");
    } catch (e) {
      body.innerHTML = `<tr><td colspan="2" class="text-center text-danger">Error</td></tr>`;
    }
  }

  async function pintarGraficas() {
    try {
      const [hRes, dRes] = await Promise.all([
        fetch(`/api/ventas-por-hora${qs()}`),
        fetch(`/api/ventas-por-dia${qs()}`)
      ]);
      const horas = await hRes.json();
      const dias  = await dRes.json();

      // Hora
      if (chartHora) chartHora.destroy();
      chartHora = new Chart(document.getElementById("chart-hora"), {
        type: "bar",
        data: {
          labels: horas.map(x => x.hora),
          datasets: [{ label: "Ventas", data: horas.map(x => x.ventas) }]
        }
      });

      // Día
      if (chartDia) chartDia.destroy();
      chartDia = new Chart(document.getElementById("chart-dia"), {
        type: "bar",
        data: {
          labels: dias.map(x => x.dia),
          datasets: [{ label: "Ventas", data: dias.map(x => x.ventas) }]
        }
      });
    } catch (e) {
      console.error(e);
    }
  }

  function prepararFormulario() {
    const form = document.getElementById("form-predict");
    const spin = document.getElementById("spin");
    const btn  = document.getElementById("btn-predict");
    const out  = document.getElementById("pred-resultado");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const producto_id = Number(document.getElementById("sel-producto").value);
      const dias_futuro = Number(document.getElementById("inp-dias").value);
      try {
        spin.classList.remove("d-none");
        btn.setAttribute("disabled", "disabled");

        const r = await fetch("/api/demanda", {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify({ producto_id, dias_futuro })
        });
        const j = await r.json();

        if (j.error) out.textContent = `⚠ ${j.error}`;
        else out.textContent = `Demanda estimada: ${j.demanda_estimada} (promedio diario: ${j.promedio_diario})`;
      } catch {
        out.textContent = "Error de conexión";
      } finally {
        spin.classList.add("d-none");
        btn.removeAttribute("disabled");
      }
    });
  }

  async function refreshAll() {
    await Promise.all([pintarKPIs(), pintarTopProductos(), pintarGraficas()]);
  }

  // Primera carga
  refreshAll();
});
