document.addEventListener("DOMContentLoaded", () => {
  pintarKPIs();
  pintarTopProductos();
  prepararFormulario();
  pintarGraficas();
});

function toast(msg, tipo = "primary") {
  const el = document.getElementById("toast");
  el.className = `toast text-bg-${tipo}`;
  document.getElementById("toast-body").textContent = msg;
  const t = new bootstrap.Toast(el);
  t.show();
}

function fmtMoney(n) {
  return new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(n);
}

/* KPIs */
async function pintarKPIs() {
  try {
    const r = await fetch("/api/kpis");
    const j = await r.json();
    document.getElementById("kpi-ventas-mes").textContent = fmtMoney(j.ventas_mes || 0);
    document.getElementById("kpi-crecimiento").textContent = `${(j.crecimiento ?? 0).toFixed(1)}%`;
    document.getElementById("kpi-ticket").textContent = fmtMoney(j.ticket_promedio || 0);
    document.getElementById("kpi-clientes").textContent = j.clientes_unicos ?? 0;
  } catch (e) {
    toast("No se pudieron cargar KPIs", "danger");
  }
}

/* Top productos */
async function pintarTopProductos() {
  const body = document.getElementById("top-body");
  try {
    const r = await fetch("/api/top-productos?limite=10");
    const arr = await r.json();
    if (!arr.length) {
      body.innerHTML = `<tr><td colspan="2" class="text-center text-secondary">Sin datos</td></tr>`;
      return;
    }
    body.innerHTML = arr
      .map(r => `<tr><td>${r.nombre || r.producto}</td><td class="text-end">${fmtMoney(r.monto || r.ingreso || 0)}</td></tr>`)
      .join("");
  } catch (e) {
    body.innerHTML = `<tr><td colspan="2" class="text-center text-danger">Error</td></tr>`;
  }
}

/* Form predicción */
function prepararFormulario() {
  const form = document.getElementById("form-predict");
  const spin = document.getElementById("spin");
  const btn = document.getElementById("btn-predict");
  const out = document.getElementById("resultado");

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

      if (j.error) {
        out.textContent = `⚠ ${j.error}`;
        toast("No hay suficientes datos para ese producto", "warning");
      } else {
        out.textContent = `Demanda estimada: ${j.demanda_estimada} (promedio diario: ${j.promedio_diario})`;
        toast("Predicción lista", "success");
      }
    } catch (e2) {
      out.textContent = "Error de conexión";
      toast("Error al predecir", "danger");
    } finally {
      spin.classList.add("d-none");
      btn.removeAttribute("disabled");
    }
  });
}

/* Gráficas con Chart.js */
async function pintarGraficas() {
  try {
    const [hRes, dRes] = await Promise.all([
      fetch("/api/ventas-por-hora"),
      fetch("/api/ventas-por-dia")
    ]);
    const horas = await hRes.json();
    const dias  = await dRes.json();

    new Chart(document.getElementById("chart-hora"), {
      type: "bar",
      data: {
        labels: horas.map(x => x.hora),
        datasets: [{ label: "Ventas", data: horas.map(x => x.ventas) }]
      }
    });

    new Chart(document.getElementById("chart-dia"), {
      type: "bar",
      data: {
        labels: dias.map(x => x.dia),
        datasets: [{ label: "Ventas", data: dias.map(x => x.ventas) }]
      }
    });
  } catch {
    // opcional: sin toast para no molestar al usuario si no hay datos aún
  }
}
