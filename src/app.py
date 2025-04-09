import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, User, Personaje, Planeta, Vehiculo, Favorito
from werkzeug.security import generate_password_hash
from datetime import datetime

# Definimos la clase StarWarsData aquí (no modificada)
class StarWarsData:
    personajes = [
        {"nombre": "Luke Skywalker", "genero": "masculino", "altura": 172, "color_pelo": "rubio", "color_piel": "clara", "color_ojos": "azul"},
        {"nombre": "Leia Organa", "genero": "femenino", "altura": 150, "color_pelo": "castaño", "color_piel": "clara", "color_ojos": "marrón"},
        {"nombre": "Darth Vader", "genero": "masculino", "altura": 202, "color_pelo": "ninguno", "color_piel": "clara", "color_ojos": "amarillo"},
        {"nombre": "Yoda", "genero": "masculino", "altura": 66, "color_pelo": "blanco", "color_piel": "verde", "color_ojos": "verde"},
        {"nombre": "Han Solo", "genero": "masculino", "altura": 180, "color_pelo": "castaño", "color_piel": "clara", "color_ojos": "marrón"},
        {"nombre": "Rey", "genero": "femenino", "altura": 170, "color_pelo": "castaño", "color_piel": "clara", "color_ojos": "avellana"},
        {"nombre": "Obi-Wan Kenobi", "genero": "masculino", "altura": 182, "color_pelo": "castaño", "color_piel": "clara", "color_ojos": "azul"},
    ]

    planetas = [
        {"nombre": "Tatooine", "clima": "árido", "terreno": "desierto", "poblacion": 200000},
        {"nombre": "Alderaan", "clima": "templado", "terreno": "montañas", "poblacion": 2000000000},
        {"nombre": "Hoth", "clima": "helado", "terreno": "nieve", "poblacion": "desconocida"},
        {"nombre": "Dagobah", "clima": "húmedo", "terreno": "pantano", "poblacion": "desconocida"},
        {"nombre": "Endor", "clima": "templado", "terreno": "bosques", "poblacion": 30000},
        {"nombre": "Naboo", "clima": "templado", "terreno": "lagos", "poblacion": 4500000000},
        {"nombre": "Coruscant", "clima": "urbano", "terreno": "ciudad", "poblacion": 1000000000000},
    ]

    vehiculos = [
        {"nombre": "X-Wing", "modelo": "T-65", "fabricante": "Incom Corporation", "costo": 149999, "longitud": 12.5},
        {"nombre": "TIE Fighter", "modelo": "Twin Ion Engine", "fabricante": "Sienar Fleet Systems", "costo": 75000, "longitud": 8.99},
        {"nombre": "Millennium Falcon", "modelo": "YT-1300", "fabricante": "Corellian Engineering", "costo": 100000, "longitud": 34.75},
        {"nombre": "AT-AT", "modelo": "All Terrain Armored Transport", "fabricante": "Kuat Drive Yards", "costo": "unknown", "longitud": 20},
        {"nombre": "Slave I", "modelo": "Firespray-31", "fabricante": "Kuat Systems", "costo": 120000, "longitud": 21.5},
        {"nombre": "Speeder Bike", "modelo": "74-Z", "fabricante": "Aratech Repulsor Company", "costo": 8000, "longitud": 3},
        {"nombre": "Jedi Starfighter", "modelo": "Delta-7", "fabricante": "Kuat Systems", "costo": 180000, "longitud": 8},
    ]

# Configuración de Flask y base de datos
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///starwars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return jsonify({"mensaje": "API de Star Wars funcionando"}), 200

@app.route('/usuarios', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    try:
        data = request.json

        # Validamos que todos los datos necesarios estén presentes
        if not data or 'email' not in data or 'password' not in data or 'nombre' not in data:
            return jsonify({"error": "Datos incompletos"}), 400

        # Validamos que la contraseña no sea vacía
        if not data['password']:
            return jsonify({"error": "La contraseña es obligatoria"}), 400

        # Ciframos la contraseña antes de guardarla
        hashed_password = generate_password_hash(data['password'])  # Usando el método predeterminado pbkdf2:sha256

        # Crear el usuario con los datos proporcionados
        nuevo_usuario = User(
            email=data['email'],
            password=hashed_password,  # Contraseña cifrada
            nombre=data['nombre'],
            apellido=data.get('apellido', ''),  # En caso de que apellido no sea proporcionado
            fecha_suscripcion=datetime.utcnow()
        )
        
        # Agregar el nuevo usuario a la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({"message": "Usuario creado exitosamente"}), 201

    except Exception as e:
        print(f"Error interno del servidor: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route('/populate', methods=['POST'])
def populate_data():
    # Verificamos si la tabla ya tiene datos
    if Personaje.query.first(): 
        return jsonify({"message": "Ya poblado"}), 400

    # Añadimos los personajes a la base de datos
    for p in StarWarsData.personajes:
        db.session.add(Personaje(**p))
    
    # Añadimos los planetas
    for pl in StarWarsData.planetas:
        db.session.add(Planeta(**pl))
    
    # Añadimos los vehículos
    for v in StarWarsData.vehiculos:
        db.session.add(Vehiculo(**v))

    # Commit de los cambios en la base de datos
    db.session.commit()
    
    return jsonify({"message": "Base de datos poblada con éxito"}), 201

@app.route('/personajes', methods=['GET'])
def get_personajes():
    personajes = Personaje.query.all()
    return jsonify([p.serialize() for p in personajes]), 200

@app.route('/personajes/<int:id>', methods=['GET'])
def get_personaje(id):
    personaje = Personaje.query.get_or_404(id)
    return jsonify(personaje.serialize()), 200

@app.route('/planetas', methods=['GET'])
def get_planetas():
    planetas = Planeta.query.all()
    return jsonify([p.serialize() for p in planetas]), 200

@app.route('/planetas/<int:id>', methods=['GET'])
def get_planeta(id):
    planeta = Planeta.query.get_or_404(id)
    return jsonify(planeta.serialize()), 200

@app.route('/vehiculos', methods=['GET'])
def get_vehiculos():
    vehiculos = Vehiculo.query.all()
    return jsonify([v.serialize() for v in vehiculos]), 200

@app.route('/vehiculos/<int:id>', methods=['GET'])
def get_vehiculo(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    return jsonify(vehiculo.serialize()), 200

@app.route('/favoritos', methods=['GET'])
def get_all_favoritos():
    favoritos = Favorito.query.all()
    return jsonify([f.serialize() for f in favoritos]), 200


@app.route('/favoritos', methods=['POST'])
def add_favorito():
    data = request.json

    # Verificamos que los campos necesarios estén presentes
    if not data or 'user_id' not in data or 'tipo' not in data or 'elemento_id' not in data:
        return jsonify({"error": "Datos incompletos"}), 400

    # Verificamos que el usuario exista
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Verificamos que el elemento exista, en este caso un planeta
    if data['tipo'] == 'planeta':
        elemento = Planeta.query.get(data['elemento_id'])
        if not elemento:
            return jsonify({"error": "Planeta no encontrado"}), 404
    else:
        return jsonify({"error": "Tipo de favorito no soportado"}), 400

    # Crear el objeto Favorito con los datos proporcionados
    favorito = Favorito(
        user_id=data['user_id'],
        tipo=data['tipo'],
        elemento_id=data['elemento_id']
    )

    # Añadimos el favorito a la base de datos
    db.session.add(favorito)
    db.session.commit()

    return jsonify({"message": "Favorito agregado exitosamente"}), 201


@app.route('/favoritos/<int:user_id>', methods=['GET'])
def get_favoritos(user_id):
    favoritos = Favorito.query.filter_by(user_id=user_id).all()
    return jsonify([f.serialize() for f in favoritos]), 200


@app.route('/populate_starwars_data', methods=['POST'])
def populate_starwars_data():
    # Primero, verificamos si los datos ya están en la base de datos para evitar duplicados.
    if Personaje.query.first() or Planeta.query.first() or Vehiculo.query.first():
        return jsonify({"message": "Los datos ya están poblados en la base de datos."}), 400
    
    # Insertar personajes
    for p in StarWarsData.personajes:
        personaje = Personaje(
            nombre=p['nombre'],
            genero=p['genero'],
            altura=str(p['altura']),  # Asumiendo que 'altura' es un número, lo convertimos a string
            color_pelo=p['color_pelo'],
            color_piel=p['color_piel'],
            color_ojos=p['color_ojos']
        )
        db.session.add(personaje)

    # Insertar planetas
    for pl in StarWarsData.planetas:
        planeta = Planeta(
            nombre=pl['nombre'],
            clima=pl['clima'],
            terreno=pl['terreno'],
            poblacion=str(pl['poblacion'])  # Asegurándonos de convertir 'poblacion' a string
        )
        db.session.add(planeta)

    # Insertar vehículos
    for v in StarWarsData.vehiculos:
        vehiculo = Vehiculo(
            nombre=v['nombre'],
            modelo=v['modelo'],
            fabricante=v['fabricante'],
            costo=str(v['costo']),  # Convertir costo a string
            longitud=str(v['longitud'])  # Convertir longitud a string
        )
        db.session.add(vehiculo)

    # Confirmar la transacción para guardar los datos
    db.session.commit()
    
    return jsonify({"message": "Datos de Star Wars agregados exitosamente"}), 201

# Solo se ejecuta si `$ python src/app.py` se ejecuta
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
