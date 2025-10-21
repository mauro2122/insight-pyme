document.addEventListener("DOMContentLoaded", () => {
  cargarKPIs();
  cargarTopProductos();

  const form = document.getElementById("form-demanda");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const productoId = Number(document.getElementById("producto-id").value);
    const dias = Number(document.getElementById("dias").value);
    const salida = document.getElementById("resultado");
    salida.textContent = "Calculando...";

    try {
      const resp = await fetch("/api/demanda", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ producto_id: productoId, dias_futuro: dias })
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      salida.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
      salida.textContent = `Error: ${err.message}`;
      console.error(err);
    }
  });
});

async function cargarKPIs() {
  try {
    const r = await fetch("/api/kpis");
    const d = await r.json();
    document.getElementById("kpi-clientes").textContent = d.clientes ?? 0;
    document.getElementById("kpi-productos").textContent = d.productos ?? 0;
    document.getElementById("kpi-ventas").textContent = (d.ventas_total ?? 0).toFixed(2);
  } catch (e) { console.error(e); }
}

async function cargarTopProductos() {
  try {
    const r = await fetch("/api/top-productos?limite=5");
    const d = await r.json();
    const cont = document.getElementById("top-productos");
    cont.innerHTML = "";
    d.forEach((it) => {
      const li = document.createElement("li");
      li.textContent = `${it.nombre} — ${Number(it.monto).toFixed(2)}`;
      cont.appendChild(li);
    });
  } catch (e) { console.error(e); }
}
