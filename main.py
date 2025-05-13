import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from flask import make_response
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:48481012al@localhost:5432/hoteldb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------- MODELOS ----------------

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    documento_identidad = db.Column(db.String(50), unique=True, nullable=False)
    fecha_registro = db.Column(db.Date, default=datetime.utcnow)

class Habitacion(db.Model):
    __tablename__ = 'habitaciones'
    id_habitacion = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    precio_noche = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), nullable=False)

class Reserva(db.Model):
    __tablename__ = 'reservas'
    id_reserva = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=False)
    id_habitacion = db.Column(db.Integer, db.ForeignKey('habitaciones.id_habitacion'), nullable=False)  # Room is required
    fecha_reserva = db.Column(db.Date, default=datetime.utcnow)
    fecha_entrada = db.Column(db.Date, nullable=False)
    fecha_salida = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), default='Confirmada')

class DetalleReserva(db.Model):
    __tablename__ = 'detalle_reserva'
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_reserva = db.Column(db.Integer, db.ForeignKey('reservas.id_reserva'), nullable=False)
    id_habitacion = db.Column(db.Integer, db.ForeignKey('habitaciones.id_habitacion'), nullable=False)
    precio_por_noche = db.Column(db.Numeric(10, 2), nullable=False)
    nro_noches = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

class Pago(db.Model):
    __tablename__ = 'pagos'
    id_pago = db.Column(db.Integer, primary_key=True)
    id_reserva = db.Column(db.Integer, db.ForeignKey('reservas.id_reserva'), nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column(db.String(20), nullable=False)
    estado_pago = db.Column(db.String(20), default='Pendiente')

class ServicioHotel(db.Model):
    __tablename__ = 'servicios_hotel'
    id_servicio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)

class ServicioExterior(db.Model):
    __tablename__ = 'servicios_exterior'
    id_servicio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    proveedor = db.Column(db.String(100))
    precio = db.Column(db.Numeric(10, 2), nullable=False)

class ServicioReserva(db.Model):
    __tablename__ = 'servicios_reserva'
    id_servicio_reserva = db.Column(db.Integer, primary_key=True)
    id_reserva = db.Column(db.Integer, db.ForeignKey('reservas.id_reserva'), nullable=False)
    id_servicio = db.Column(db.Integer, nullable=False)
    tipo_servicio = db.Column(db.String(10), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

class CheckInCheckOut(db.Model):
    __tablename__ = 'checkin_checkout'
    id_control = db.Column(db.Integer, primary_key=True)
    id_reserva = db.Column(db.Integer, db.ForeignKey('reservas.id_reserva'), nullable=False)
    fecha_checkin = db.Column(db.DateTime)
    fecha_checkout = db.Column(db.DateTime)

class Recibo(db.Model):
    __tablename__ = 'recibos'
    id_recibo = db.Column(db.Integer, primary_key=True)
    id_reserva = db.Column(db.Integer, db.ForeignKey('reservas.id_reserva'), nullable=False)
    id_pago = db.Column(db.Integer, db.ForeignKey('pagos.id_pago'), nullable=False, unique=True)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    impuestos = db.Column(db.Numeric(10, 2), default=0)
    observaciones = db.Column(db.Text)

# ---------------- ENDPOINTS ----------------

@app.route("/reservas", methods=["GET"])
def listar_reservas():  # Cambié el nombre de la función
    """
    Obtiene todas las reservas junto con la información del cliente y la habitación asociada.
    """
    try:
        # Query to join Reservas with Clientes and Habitaciones
        reservas = db.session.query(
            Reserva.id_reserva,
            Reserva.fecha_reserva,
            Reserva.fecha_entrada,
            Reserva.fecha_salida,
            Reserva.estado,
            Cliente.id_cliente,
            Cliente.nombre.label("cliente_nombre"),
            Cliente.telefono.label("cliente_telefono"),
            Habitacion.numero.label("habitacion_numero"),
            Habitacion.tipo.label("habitacion_tipo")
        ).join(Cliente, Reserva.id_cliente == Cliente.id_cliente)\
         .join(Habitacion, Reserva.id_habitacion == Habitacion.id_habitacion).all()

        # Format the result as a list of dictionaries
        resultado = [
            {
                "id_reserva": r.id_reserva,
                "fecha_reserva": r.fecha_reserva.strftime('%Y-%m-%d'),
                "fecha_entrada": r.fecha_entrada.strftime('%Y-%m-%d'),
                "fecha_salida": r.fecha_salida.strftime('%Y-%m-%d'),
                "estado": r.estado,
                "id_cliente": r.id_cliente,
                "cliente_nombre": r.cliente_nombre,
                "cliente_telefono": r.cliente_telefono,
                "habitacion_numero": r.habitacion_numero,
                "habitacion_tipo": r.habitacion_tipo
            }
            for r in reservas
        ]

        return jsonify(resultado), 200
    except Exception as e:
        logging.error(f"Error al obtener reservas: {e}")
        return jsonify({"error": "No se pudieron obtener las reservas", "detalles": str(e)}), 500
    
@app.route("/detalle_reserva", methods=["POST"])
def agregar_detalle_reserva():
    """
    Agrega un nuevo detalle de reserva.
    """
    try:
        data = request.get_json()
        nuevo_detalle = DetalleReserva(
            id_reserva=data["id_reserva"],
            id_habitacion=data["id_habitacion"],
            precio_por_noche=data["precio_por_noche"],
            nro_noches=data["nro_noches"]
        )
        db.session.add(nuevo_detalle)
        db.session.commit()
        return jsonify({"message": "Detalle de reserva agregado exitosamente"}), 201
    except Exception as e:
        logging.error(f"Error al agregar detalle de reserva: {e}")
        return jsonify({"error": "No se pudo agregar el detalle de reserva", "detalles": str(e)}), 500
    
@app.route("/clientes", methods=["POST"])
def crear_cliente():
    """
    Crea un nuevo cliente en la tabla Clientes.
    """
    try:
        # Obtener datos del cuerpo de la solicitud
        data = request.get_json()

        # Crear una nueva instancia de Cliente
        nuevo_cliente = Cliente(
            nombre=data["nombre"],
            apellido=data["apellido"],
            correo=data["correo"],
            telefono=data["telefono"],
            documento_identidad=data["documento_identidad"]
        )

        # Agregar el cliente a la base de datos
        db.session.add(nuevo_cliente)
        db.session.commit()

        # Respuesta exitosa
        return jsonify({
            "message": "Cliente creado exitosamente",
            "id_cliente": nuevo_cliente.id_cliente
        }), 201

    except Exception as e:
        # Manejo de errores
        logging.error(f"Error al crear cliente: {e}")
        return jsonify({"error": "No se pudo crear el cliente", "detalles": str(e)}), 500

@app.route("/clientes", methods=["GET"])
def obtener_clientes():
    """
    Obtiene todos los clientes.
    """
    try:
        clientes = Cliente.query.all()
        resultado = [
            {
                "id_cliente": c.id_cliente,
                "nombre": c.nombre,
                "apellido": c.apellido,
                "correo": c.correo,
                "telefono": c.telefono,
                "documento_identidad": c.documento_identidad
            }
            for c in clientes
        ]
        return jsonify(resultado), 200
    except Exception as e:
        logging.error(f"Error al obtener clientes: {e}")
        return jsonify({"error": "No se pudieron obtener los clientes", "detalles": str(e)}), 500
        
@app.route("/reservas", methods=["POST"])
def agregar_reserva():
    """
    Agrega una nueva reserva a la tabla Reservas.
    """
    try:
        # Obtener datos del cuerpo de la solicitud
        data = request.get_json()

        # Validar que el cliente existe
        cliente = Cliente.query.get(data["id_cliente"])
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404

        # Validar que la habitación existe
        habitacion = Habitacion.query.get(data["id_habitacion"])
        if not habitacion:
            return jsonify({"error": "Habitación no encontrada"}), 404

        # Crear una nueva instancia de Reserva
        nueva_reserva = Reserva(
            id_cliente=data["id_cliente"],
            id_habitacion=data["id_habitacion"],  # Include the room ID
            fecha_entrada=datetime.strptime(data["fecha_entrada"], '%Y-%m-%d'),
            fecha_salida=datetime.strptime(data["fecha_salida"], '%Y-%m-%d'),
            estado=data.get("estado", "Confirmada")  # Valor predeterminado: 'Confirmada'
        )

        # Agregar la reserva a la base de datos
        db.session.add(nueva_reserva)
        db.session.commit()

        # Respuesta exitosa
        return jsonify({
            "message": "Reserva creada exitosamente",
            "id_reserva": nueva_reserva.id_reserva
        }), 201

    except Exception as e:
        # Manejo de errores
        logging.error(f"Error al agregar reserva: {e}")
        return jsonify({"error": "No se pudo agregar la reserva", "detalles": str(e)}), 500

@app.route("/reservas/<int:id_reserva>", methods=["PUT"])
def actualizar_reserva(id_reserva):
    try:
        reserva = Reserva.query.get(id_reserva)
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404
        
        data = request.get_json()
        if "id_cliente" in data:
            reserva.id_cliente = data["id_cliente"]
        if "id_habitacion" in data:
            reserva.id_habitacion = data["id_habitacion"]
        if "fecha_entrada" in data:
            reserva.fecha_entrada = datetime.strptime(data["fecha_entrada"], '%Y-%m-%d')
        if "fecha_salida" in data:
            reserva.fecha_salida = datetime.strptime(data["fecha_salida"], '%Y-%m-%d')
        if "estado" in data:
            reserva.estado = data["estado"]
        
        db.session.commit()
        return jsonify({"message": "Reserva actualizada"}), 200
    except Exception as e:
        return jsonify({"error": "Error al actualizar la reserva", "detalles": str(e)}), 500

@app.route("/reservas/<int:id_reserva>", methods=["DELETE"])
def eliminar_reserva(id_reserva):
    try:
        reserva = Reserva.query.get(id_reserva)
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404
        
        db.session.delete(reserva)
        db.session.commit()
        return jsonify({"message": "Reserva eliminada"}), 200
    except Exception as e:
        return jsonify({"error": "Error al eliminar la reserva", "detalles": str(e)}), 500

@app.route("/habitaciones", methods=["GET"])
def obtener_habitaciones():
    habitaciones = Habitacion.query.all()
    resultado = [{"id_habitacion": h.id_habitacion, "numero": h.numero, "tipo": h.tipo, "capacidad": h.capacidad, "precio_noche": float(h.precio_noche), "estado": h.estado} for h in habitaciones]
    return jsonify(resultado), 200

@app.route("/habitaciones", methods=["POST"])
def crear_habitacion():
    try:
        data = request.get_json()
        nueva_habitacion = Habitacion(
            numero=data["numero"],
            tipo=data["tipo"],
            capacidad=data["capacidad"],
            precio_noche=data["precio_noche"],
            estado=data["estado"]
        )
        db.session.add(nueva_habitacion)
        db.session.commit()
        return jsonify({"message": "Habitación creada", "id_habitacion": nueva_habitacion.id_habitacion}), 201
    except Exception as e:
        logging.error(f"Error al crear habitación: {e}")
        return jsonify({"error": "No se pudo crear la habitación", "detalles": str(e)}), 500
    
@app.route("/checkin", methods=["POST"])
def realizar_checkin():
    """
    Realiza el check-in de una reserva.
    """
    try:
        data = request.get_json()
        nuevo_checkin = CheckInCheckOut(
            id_reserva=data["id_reserva"],
            fecha_checkin=data["fecha_checkin"]
        )
        db.session.add(nuevo_checkin)
        db.session.commit()
        return jsonify({"message": "Check-in realizado exitosamente"}), 201
    except Exception as e:
        logging.error(f"Error al realizar check-in: {e}")
        return jsonify({"error": "No se pudo realizar el check-in", "detalles": str(e)}), 500


@app.route("/checkout/<int:id_control>", methods=["PUT"])
def realizar_checkout(id_control):
    """
    Realiza el check-out de una reserva.
    """
    try:
        checkin_checkout = CheckInCheckOut.query.get(id_control)
        if not checkin_checkout:
            return jsonify({"error": "Registro de check-in/check-out no encontrado"}), 404

        data = request.get_json()
        checkin_checkout.fecha_checkout = data["fecha_checkout"]
        db.session.commit()
        return jsonify({"message": "Check-out realizado exitosamente"}), 200
    except Exception as e:
        logging.error(f"Error al realizar check-out: {e}")
        return jsonify({"error": "No se pudo realizar el check-out", "detalles": str(e)}), 500
    
@app.route("/exportar/pdf", methods=["GET"])
def exportar_pdf():
    """
    Exporta las reservas a un archivo PDF.
    """
    try:
        # Obtener las reservas
        reservas = db.session.query(
            Reserva.id_reserva,
            Reserva.fecha_reserva,
            Reserva.fecha_entrada,
            Reserva.fecha_salida,
            Reserva.estado,
            Cliente.nombre.label("cliente_nombre"),
            Cliente.apellido.label("cliente_apellido"),
            Habitacion.numero.label("habitacion_numero")
        ).join(Cliente, Reserva.id_cliente == Cliente.id_cliente)\
         .join(Habitacion, Reserva.id_habitacion == Habitacion.id_habitacion).all()

        # Crear un archivo PDF en memoria
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setTitle("Reporte de Reservas")

        # Título
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, 750, "Reporte de Reservas")

        # Encabezados
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, 700, "ID Reserva")
        pdf.drawString(120, 700, "Cliente")
        pdf.drawString(250, 700, "Habitación")
        pdf.drawString(350, 700, "Entrada")
        pdf.drawString(450, 700, "Salida")

        # Datos
        pdf.setFont("Helvetica", 10)
        y = 680
        for r in reservas:
            pdf.drawString(50, y, str(r.id_reserva))
            pdf.drawString(120, y, f"{r.cliente_nombre} {r.cliente_apellido}")
            pdf.drawString(250, y, str(r.habitacion_numero))
            pdf.drawString(350, y, r.fecha_entrada.strftime('%Y-%m-%d'))
            pdf.drawString(450, y, r.fecha_salida.strftime('%Y-%m-%d'))
            y -= 20
            if y < 50:  # Salto de página
                pdf.showPage()
                y = 750

        pdf.save()
        buffer.seek(0)

        # Enviar el PDF como respuesta
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=reporte_reservas.pdf'
        return response

    except Exception as e:
        logging.error(f"Error al exportar a PDF: {e}")
        return jsonify({"error": "No se pudo exportar el reporte a PDF", "detalles": str(e)}), 500
    
@app.route("/exportar/<string:formato>", methods=["GET"])
def exportar_datos(formato):
    """
    Exporta las reservas a un archivo Excel o CSV.
    """
    try:
        # Obtener las reservas
        reservas = db.session.query(
            Reserva.id_reserva,
            Reserva.fecha_reserva,
            Reserva.fecha_entrada,
            Reserva.fecha_salida,
            Reserva.estado,
            Cliente.nombre.label("cliente_nombre"),
            Cliente.apellido.label("cliente_apellido"),
            Habitacion.numero.label("habitacion_numero")
        ).join(Cliente, Reserva.id_cliente == Cliente.id_cliente)\
         .join(Habitacion, Reserva.id_habitacion == Habitacion.id_habitacion).all()

        # Convertir los datos a un DataFrame de pandas
        data = [
            {
                "ID Reserva": r.id_reserva,
                "Cliente": f"{r.cliente_nombre} {r.cliente_apellido}",
                "Habitación": r.habitacion_numero,
                "Fecha Entrada": r.fecha_entrada.strftime('%Y-%m-%d'),
                "Fecha Salida": r.fecha_salida.strftime('%Y-%m-%d'),
                "Estado": r.estado
            }
            for r in reservas
        ]
        df = pd.DataFrame(data)

        # Generar el archivo según el formato solicitado
        if formato == "excel":
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Reservas")
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response.headers["Content-Disposition"] = "attachment; filename=reporte_reservas.xlsx"
            return response

        elif formato == "csv":
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers["Content-Type"] = "text/csv"
            response.headers["Content-Disposition"] = "attachment; filename=reporte_reservas.csv"
            return response

        else:
            return jsonify({"error": "Formato no soportado. Use 'excel' o 'csv'."}), 400

    except Exception as e:
        logging.error(f"Error al exportar datos: {e}")
        return jsonify({"error": "No se pudo exportar el reporte", "detalles": str(e)}), 500
# ---------------- MAIN ----------------

def initialize_database():
    with app.app_context():
        db.create_all()
        print("¡Base de datos conectada y tablas sincronizadas!")

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)

