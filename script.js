const apiURL = "http://127.0.0.1:5000/reservas";
let editingReservaId = null;

document.addEventListener("DOMContentLoaded", () => {
  // Título
  const title = document.createElement("h1");
  title.textContent = "Gestión de Reservas de Hotel";
  title.style.textAlign = "center";
  document.body.appendChild(title);

  // Sección de reservas
  const reservaSection = document.createElement("section");
  reservaSection.id = "reserva-section";
  reservaSection.style = "width:80%; max-width:600px; margin:0 auto; padding:20px;";
  reservaSection.innerHTML = `<h2 style="text-align:center;">Lista de Reservas</h2><div id="reserva-list"></div>`;
  document.body.appendChild(reservaSection);

  // Sección de formulario
  const formSection = document.createElement("section");
  formSection.id = "form-section";
  formSection.style = "width:80%; max-width:600px; margin:0 auto; padding:20px;";
  formSection.innerHTML = `<h2 style="text-align:center;">Registrar Reserva</h2>`;
  
  const form = document.createElement("form");
  form.id = "reserva-form";
  form.innerHTML = `
    <label>ID Cliente: <input type="number" id="id_cliente" required></label><br>
    <label>Fecha Entrada: <input type="date" id="fecha_entrada" required></label><br>
    <label>Fecha Salida: <input type="date" id="fecha_salida" required></label><br>
    <button type="submit">Guardar Reserva</button>
  `;
  formSection.appendChild(form);
  document.body.appendChild(formSection);

  fetch(apiURL)
    .then(res => res.json())
    .then(data => renderReservas(data));

  // Envío del formulario
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const reservaData = {
      id_cliente: parseInt(document.getElementById("id_cliente").value),
      fecha_entrada: document.getElementById("fecha_entrada").value,
      fecha_salida: document.getElementById("fecha_salida").value,
    };

    const method = editingReservaId ? "PUT" : "POST";
    const url = editingReservaId ? `${apiURL}/${editingReservaId}` : apiURL;

    fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(reservaData),
    })
      .then(res => res.json())
      .then(() => {
        alert("Reserva guardada exitosamente");
        form.reset();
        editingReservaId = null;
        return fetch(apiURL).then(res => res.json()).then(renderReservas);
      })
      .catch(err => alert("Error al guardar reserva: " + err));
  });
});

function renderReservas(data) {
  const list = document.getElementById("reserva-list");
  list.innerHTML = "";

  if (!data.length) {
    list.innerText = "No hay reservas registradas.";
    return;
  }

  data.forEach(r => {
    const div = document.createElement("div");
    div.style = "border:1px solid #ccc; padding:10px; margin-bottom:10px; border-radius:5px;";

    div.innerHTML = `
      <p><strong>ID Cliente:</strong> ${r.id_cliente}</p>
      <p><strong>Entrada:</strong> ${r.fecha_entrada}</p>
      <p><strong>Salida:</strong> ${r.fecha_salida}</p>
      <p><strong>Estado:</strong> ${r.estado}</p>
    `;

    const editBtn = document.createElement("button");
    editBtn.innerText = "Editar";
    editBtn.style.marginRight = "10px";
    editBtn.onclick = () => {
      document.getElementById("id_cliente").value = r.id_cliente;
      document.getElementById("fecha_entrada").value = r.fecha_entrada;
      document.getElementById("fecha_salida").value = r.fecha_salida;
      editingReservaId = r.id_reserva;
    };

    const deleteBtn = document.createElement("button");
    deleteBtn.innerText = "Eliminar";
    deleteBtn.style.background = "red";
    deleteBtn.style.color = "white";
    deleteBtn.onclick = () => {
      if (confirm("¿Estás seguro de eliminar esta reserva?")) {
        fetch(`${apiURL}/${r.id_reserva}`, { method: "DELETE" })
          .then(() => {
            alert("Reserva eliminada.");
            return fetch(apiURL).then(res => res.json()).then(renderReservas);
          })
          .catch(err => alert("Error al eliminar reserva: " + err));
      }
    };

    div.appendChild(editBtn);
    div.appendChild(deleteBtn);
    list.appendChild(div);
  });
}
