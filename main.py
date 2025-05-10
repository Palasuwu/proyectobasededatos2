import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2604@localhost:5432/hoteldb'
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
def obtener_reservas():
    reservas = Reserva.query.all()
    resultado = []
    for r in reservas:
        resultado.append({
            "id_reserva": r.id_reserva,
            "id_cliente": r.id_cliente,
            "fecha_reserva": r.fecha_reserva.isoformat(),
            "fecha_entrada": r.fecha_entrada.isoformat(),
            "fecha_salida": r.fecha_salida.isoformat(),
            "estado": r.estado
        })
    return jsonify(resultado), 200

@app.route("/clientes", methods=["POST"])
def crear_cliente():
    try:
        data = request.get_json()
        nuevo_cliente = Cliente(
            nombre=data["nombre"],
            apellido=data["apellido"],
            correo=data["correo"],
            telefono=data["telefono"],
            documento_identidad=data["documento_identidad"]
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        return jsonify({"message": "Cliente creado", "id_cliente": nuevo_cliente.id_cliente}), 201
    except Exception as e:
        logging.error(f"Error al crear cliente: {e}")
        return jsonify({"error": "No se pudo crear el cliente", "detalles": str(e)}), 500

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

        # Crear una nueva instancia de Reserva
        nueva_reserva = Reserva(
            id_cliente=data["id_cliente"],
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

# ---------------- MAIN ----------------

def initialize_database():
    with app.app_context():
        db.create_all()
        print("¡Base de datos conectada y tablas sincronizadas!")

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)

