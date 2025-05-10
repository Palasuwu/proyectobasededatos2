const apiURL = "http://127.0.0.1:5000/reservas";
let editingReservaId = null;

document.addEventListener("DOMContentLoaded", () => {
  // Apply global styles
  document.body.style.fontFamily = "Arial, sans-serif";
  document.body.style.margin = "0";
  document.body.style.padding = "0";
  document.body.style.backgroundColor = "#f9f9f9";

  // Título
  const title = document.createElement("h1");
  title.textContent = "Gestión de Reservas de Hotel";
  title.style.textAlign = "center";
  title.style.padding = "20px";
  title.style.backgroundColor = "#4CAF50";
  title.style.color = "white";
  document.body.appendChild(title);

  // Sección de reservas
  const reservaSection = document.createElement("section");
  reservaSection.id = "reserva-section";
  reservaSection.style = `
    width: 80%; 
    max-width: 600px; 
    margin: 20px auto; 
    padding: 20px; 
    background: white; 
    border-radius: 8px; 
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  `;
  reservaSection.innerHTML = `<h2 style="text-align:center; color:#333;">Lista de Reservas</h2><div id="reserva-list"></div>`;
  document.body.appendChild(reservaSection);

  // Sección de formulario
  const formSection = document.createElement("section");
  formSection.id = "form-section";
  formSection.style = `
    width: 80%; 
    max-width: 600px; 
    margin: 20px auto; 
    padding: 20px; 
    background: white; 
    border-radius: 8px; 
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  `;
  formSection.innerHTML = `<h2 style="text-align:center; color:#333;">Registrar Reserva</h2>`;
  
  const form = document.createElement("form");
  form.id = "reserva-form";
  form.style.display = "flex";
  form.style.flexDirection = "column";
  form.style.gap = "10px";
  form.innerHTML = `
    <label>ID Cliente: <input type="number" id="id_cliente" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;"></label>
    <label>Fecha Entrada: <input type="date" id="fecha_entrada" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;"></label>
    <label>Fecha Salida: <input type="date" id="fecha_salida" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;"></label>
    <label>Estado: 
      <select id="estado" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
        <option value="Confirmada">Confirmada</option>
        <option value="Cancelada">Cancelada</option>
        <option value="Finalizada">Finalizada</option>
      </select>
    </label>
    <button type="submit" style="padding:10px; background:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer;">Guardar Reserva</button>
  `;
  formSection.appendChild(form);
  document.body.appendChild(formSection);

  // Fetch and render reservations
  fetch(apiURL)
    .then(res => res.json())
    .then(data => renderReservas(data))
    .catch(err => alert("Error al cargar reservas: " + err));

  // Form submission
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const reservaData = {
      id_cliente: parseInt(document.getElementById("id_cliente").value),
      fecha_entrada: document.getElementById("fecha_entrada").value,
      fecha_salida: document.getElementById("fecha_salida").value,
      estado: document.getElementById("estado").value,
    };

    const method = editingReservaId ? "PUT" : "POST";
    const url = editingReservaId ? `${apiURL}/${editingReservaId}` : apiURL;

    fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(reservaData),
    })
      .then(res => {
        console.log("Response status:", res.status);
        return res.json();
      })
      .then(response => {
        if (response.error) {
          console.error("Error response:", response);
          alert("Error: " + response.detalles);
        } else {
          console.log("Success response:", response);
          alert("Reserva guardada exitosamente");
          form.reset();
          editingReservaId = null;
          return fetch(apiURL).then(res => res.json()).then(renderReservas);
        }
      })
      .catch(err => {
        console.error("Fetch error:", err);
        alert("Error al guardar reserva: " + err);
      });
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
    div.style = `
      border: 1px solid #ccc; 
      padding: 10px; 
      margin-bottom: 10px; 
      border-radius: 5px; 
      background: #f9f9f9;
    `;

    div.innerHTML = `
      <p><strong>ID Cliente:</strong> ${r.id_cliente}</p>
      <p><strong>Entrada:</strong> ${r.fecha_entrada}</p>
      <p><strong>Salida:</strong> ${r.fecha_salida}</p>
      <p><strong>Estado:</strong> ${r.estado}</p>
    `;

    const editBtn = document.createElement("button");
    editBtn.innerText = "Editar";
    editBtn.style = `
      margin-right: 10px; 
      padding: 5px 10px; 
      background: #2196F3; 
      color: white; 
      border: none; 
      border-radius: 4px; 
      cursor: pointer;
    `;
    editBtn.onclick = () => {
      document.getElementById("id_cliente").value = r.id_cliente;
      document.getElementById("fecha_entrada").value = r.fecha_entrada;
      document.getElementById("fecha_salida").value = r.fecha_salida;
      document.getElementById("estado").value = r.estado;
      editingReservaId = r.id_reserva;
    };

    const deleteBtn = document.createElement("button");
    deleteBtn.innerText = "Eliminar";
    deleteBtn.style = `
      padding: 5px 10px; 
      background: red; 
      color: white; 
      border: none; 
      border-radius: 4px; 
      cursor: pointer;
    `;
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
