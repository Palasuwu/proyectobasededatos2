const apiURL = "http://127.0.0.1:5000/reservas";
let editingReservaId = null;
//
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

   // Add search bar
  const searchBar = document.createElement("div");
  searchBar.style = "margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap;";
  searchBar.innerHTML = `
    <input type="text" id="search-name" placeholder="Buscar por nombre" style="flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
    <input type="text" id="search-room" placeholder="Buscar por habitación" style="flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
    <select id="search-status" style="flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
      <option value="">Buscar por estado</option>
      <option value="Confirmada">Confirmada</option>
      <option value="Cancelada">Cancelada</option>
      <option value="Finalizada">Finalizada</option>
    </select>
  `;
  reservaSection.appendChild(searchBar);

  // Add reservation list container
  reservaSection.innerHTML += `<h2 style="text-align:center; color:#333;">Lista de Reservas</h2><div id="reserva-list"></div>`;
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
    <label>Cliente: 
  <select id="id_cliente" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
    <option value="" disabled selected>Seleccione un cliente</option>
  </select>
</label>
    <label>Fecha Entrada: <input type="date" id="fecha_entrada" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;"></label>
    <label>Fecha Salida: <input type="date" id="fecha_salida" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;"></label>
    <label>Estado: 
      <select id="estado" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
        <option value="Confirmada">Confirmada</option>
        <option value="Cancelada">Cancelada</option>
        <option value="Finalizada">Finalizada</option>
      </select>
    </label>
    <label>Habitación: 
      <select id="id_habitacion" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;"></select>
    </label>
    <button type="submit" style="padding:10px; background:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer;">Guardar Reserva</button>
  `;
  formSection.appendChild(form);
  document.body.appendChild(formSection);

  // Botones para exportar reportes
const reportButtons = document.createElement("div");
reportButtons.id = "report-buttons";
reportButtons.style = "margin: 20px; text-align: center;";
reportButtons.innerHTML = `
  <button id="download-pdf" style="padding: 10px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Descargar PDF</button>
  <button id="download-excel" style="padding: 10px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer;">Descargar Excel</button>
  <button id="download-csv" style="padding: 10px; background: #FF9800; color: white; border: none; border-radius: 4px; cursor: pointer;">Descargar CSV</button>
`;
document.body.appendChild(reportButtons);

  // Fetch cientes disponibles y llenar el dropdown
fetch("http://127.0.0.1:5000/clientes")
  .then(res => res.json())
  .then(clientes => {
    const clientSelect = document.getElementById("id_cliente");
    clientes.forEach(cliente => {
      const option = document.createElement("option");
      option.value = cliente.id_cliente;
      option.textContent = `${cliente.nombre} ${cliente.apellido}`;
      clientSelect.appendChild(option);
    });
  })
  .catch(err => console.error("Error al cargar clientes:", err));

  // Sección de clientes
  const clientSection = document.createElement("section");
  clientSection.id = "client-section";
  clientSection.style = `
    width: 80%; 
    max-width: 600px; 
    margin: 20px auto; 
    padding: 20px; 
    background: white; 
    border-radius: 8px; 
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  `;
  clientSection.innerHTML = `<h2 style="text-align:center; color:#333;">Registrar Cliente</h2>`;

  const clientForm = document.createElement("form");
  clientForm.id = "client-form";
  clientForm.style.display = "flex";
  clientForm.style.flexDirection = "column";
  clientForm.style.gap = "10px";
  clientForm.innerHTML = `
    <label>Nombre: <input type="text" id="nombre" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;"></label>
    <label>Apellido: <input type="text" id="apellido" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;"></label>
    <label>Correo: <input type="email" id="correo" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;"></label>
    <label>Teléfono: <input type="text" id="telefono" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;"></label>
    <label>Documento de Identidad: <input type="text" id="documento_identidad" required style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;"></label>
    <button type="submit" style="padding:10px; background:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer;">Guardar Cliente</button>
  `;
  clientSection.appendChild(clientForm);
  document.body.appendChild(clientSection);

  // Fetch and render reservations
  fetch(apiURL)
    .then(res => res.json())
    .then(data => {
      renderReservas(data);

      // Add live search functionality
      const searchName = document.getElementById("search-name");
      const searchRoom = document.getElementById("search-room");
      const searchStatus = document.getElementById("search-status");

      [searchName, searchRoom, searchStatus].forEach(input => {
        input.addEventListener("input", () => filterReservations(data));
      });
    })
    .catch(err => alert("Error al cargar reservas: " + err));

  // Fetch available rooms and populate the dropdown
  fetch("http://127.0.0.1:5000/habitaciones")
    .then(res => res.json())
    .then(habitaciones => {
      const roomSelect = document.getElementById("id_habitacion");
      habitaciones.forEach(habitacion => {
        const option = document.createElement("option");
        option.value = habitacion.id_habitacion;
        option.textContent = `${habitacion.numero} - ${habitacion.tipo}`;
        roomSelect.appendChild(option);
      });
    })
    .catch(err => console.error("Error al cargar habitaciones:", err));

  // Form submission
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const reservaData = {
      id_cliente: parseInt(document.getElementById("id_cliente").value),
      cliente_nombre: document.getElementById("nombre").value,
      fecha_entrada: document.getElementById("fecha_entrada").value,
      fecha_salida: document.getElementById("fecha_salida").value,
      estado: document.getElementById("estado").value,
      id_habitacion: parseInt(document.getElementById("id_habitacion").value),
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

  clientForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const clientData = {
      nombre: document.getElementById("nombre").value,
      apellido: document.getElementById("apellido").value,
      correo: document.getElementById("correo").value,
      telefono: document.getElementById("telefono").value,
      documento_identidad: document.getElementById("documento_identidad").value,
    };

    fetch("http://127.0.0.1:5000/clientes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(clientData),
    })
      .then((res) => res.json())
      .then((response) => {
        if (response.error) {
          console.error("Error response:", response);
          alert("Error: " + response.detalles);
        } else {
          console.log("Success response:", response);
          alert("Cliente guardado exitosamente");
          clientForm.reset();
        }
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        alert("Error al guardar cliente: " + err);
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
    div.classList.add("reserva-item"); // Add a class for filtering
    div.dataset.clienteNombre = r.cliente_nombre.toLowerCase(); // Store data for filtering
    div.dataset.habitacionNumero = r.habitacion_numero.toLowerCase();
    div.dataset.estado = r.estado;

    div.style = `
      border: 1px solid #ccc; 
      padding: 10px; 
      margin-bottom: 10px; 
      border-radius: 5px; 
      background: #f9f9f9;
    `;

    // Create editable fields for reservation details
    div.innerHTML = `
  <p><strong>ID Reserva:</strong> ${r.id_reserva}</p>
  <p><strong>Cliente:</strong> ${r.cliente_nombre}</p>
  <p><strong>Teléfono:</strong> ${r.cliente_telefono}</p>
  <p><strong>Habitación:</strong> ${r.habitacion_numero}</p>
  <p><strong>Entrada:</strong> ${r.fecha_entrada}</p>
  <p><strong>Salida:</strong> ${r.fecha_salida}</p>
  <p><strong>Estado:</strong> ${r.estado}</p>
  <p><strong>Subtotal:</strong> $${(r.subtotal || 0).toFixed(2)}</p>
`;
    // Add Edit button
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
      // Enable editing for the fields
      document.getElementById(`cliente_nombre_${r.id_reserva}`).disabled = false;
      document.getElementById(`cliente_telefono_${r.id_reserva}`).disabled = false;
      document.getElementById(`habitacion_numero_${r.id_reserva}`).disabled = false;
      document.getElementById(`fecha_entrada_${r.id_reserva}`).disabled = false;
      document.getElementById(`fecha_salida_${r.id_reserva}`).disabled = false;
      document.getElementById(`estado_${r.id_reserva}`).disabled = false;

      // Show the Update button
      updateBtn.style.display = "inline-block";
      editBtn.style.display = "none";
    };

    // Add Update button
    const updateBtn = document.createElement("button");
    updateBtn.innerText = "Actualizar";
    updateBtn.style = `
      margin-right: 10px; 
      padding: 5px 10px; 
      background: #4CAF50; 
      color: white; 
      border: none; 
      border-radius: 4px; 
      cursor: pointer;
      display: none;
    `;
    updateBtn.onclick = () => {
      // Collect updated data
      const updatedData = {
        cliente_nombre: document.getElementById(`cliente_nombre_${r.id_reserva}`).value,
        cliente_telefono: document.getElementById(`cliente_telefono_${r.id_reserva}`).value,
        habitacion_numero: document.getElementById(`habitacion_numero_${r.id_reserva}`).value,
        fecha_entrada: document.getElementById(`fecha_entrada_${r.id_reserva}`).value,
        fecha_salida: document.getElementById(`fecha_salida_${r.id_reserva}`).value,
        estado: document.getElementById(`estado_${r.id_reserva}`).value,
      };

      // Send the updated data to the backend
      fetch(`${apiURL}/${r.id_reserva}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedData),
      })
        .then(res => res.json())
        .then(response => {
          if (response.error) {
            console.error("Error response:", response);
            alert("Error: " + response.detalles);
          } else {
            alert("Reserva actualizada exitosamente");
            return fetch(apiURL).then(res => res.json()).then(renderReservas);
          }
        })
        .catch(err => {
          console.error("Fetch error:", err);
          alert("Error al actualizar reserva: " + err);
        });
    };

    // Add Delete button
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

    // Append buttons to the reservation card
    div.appendChild(editBtn);
    div.appendChild(updateBtn);
    div.appendChild(deleteBtn);

    // Append the reservation card to the list
    list.appendChild(div);
  });
}

function filterReservations(data) {
  const searchName = document.getElementById("search-name").value.toLowerCase();
  const searchRoom = document.getElementById("search-room").value.toLowerCase();
  const searchStatus = document.getElementById("search-status").value;

  const reservations = document.querySelectorAll(".reserva-item");

  reservations.forEach(reserva => {
    const matchesName = reserva.dataset.clienteNombre.includes(searchName);
    const matchesRoom = reserva.dataset.habitacionNumero.includes(searchRoom);
    const matchesStatus = !searchStatus || reserva.dataset.estado === searchStatus;

    if (matchesName && matchesRoom && matchesStatus) {
      reserva.style.display = "block";
    } else {
      reserva.style.display = "none";
    }
  });
}
document.getElementById("download-pdf").addEventListener("click", () => {
  fetch("http://127.0.0.1:5000/exportar/pdf")
    .then(response => {
      if (!response.ok) {
        throw new Error("Error al descargar el PDF");
      }
      return response.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = "reporte_reservas.pdf";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    })
    .catch(err => alert(err.message));
});

document.getElementById("download-excel").addEventListener("click", () => {
  fetch("http://127.0.0.1:5000/exportar/excel")
    .then(response => {
      if (!response.ok) {
        throw new Error("Error al descargar el archivo Excel");
      }
      return response.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = "reporte_reservas.xlsx";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    })
    .catch(err => alert(err.message));
});

document.getElementById("download-csv").addEventListener("click", () => {
  fetch("http://127.0.0.1:5000/exportar/csv")
    .then(response => {
      if (!response.ok) {
        throw new Error("Error al descargar el archivo CSV");
      }
      return response.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = "reporte_reservas.csv";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    })
    .catch(err => alert(err.message));
});
