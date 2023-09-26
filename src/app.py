"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites, Characters, Planets, Vehicles
#from models import Person

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this "super secret" with something else!
jwt = JWTManager(app)

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#Login/Register Endpoints

@app.route("/login", methods=["POST"])
def login_user():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(username=username, password=password).first()
    
    if user is None :
        return jsonify({"msg": "Wrong username or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({ "token": access_token, "user_id": user.id })

@app.route('/register', methods=['POST'])
def register_new_user():
    if request.method == 'POST':
        user = User()
        user.username = request.get_json()['username']
        user.firstname = request.get_json()['firstname']
        user.lastname = request.get_json()['lastname']
        user.email = request.get_json()['email']
        user.password = request.get_json()['password']

        db.session.add(user)
        db.session.commit()

        # Show the updated version of the favorites
        users = []
        db_result = User.query.all()
        for item in db_result:
            users.append(item.serialize())
        return jsonify(users), 200
    
    return "Error Ocurred. Remember to add a username, firstname, lastname, email and password!", 404


#Users Endpoints

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    if request.method == 'GET':
        users = []
        db_result = User.query.all()
        for item in db_result:
            users.append(item.serialize())
        return jsonify(users), 200
    
    return "Invalid Method", 404

@app.route('/users/favorites', methods=['GET'])
@jwt_required()
def get_user_favorites():
    if request.method == 'GET':
        favorites = []
        db_result = Favorites.query.all()
        for item in db_result:
            favorites.append(item.serialize())
        return jsonify(favorites), 200
    
    return "Invalid Method", 404

#People/Characters Endpoints

@app.route('/people', methods=['GET'])
@jwt_required()
def get_people():
    if request.method == 'GET':
        people = []
        db_result = Characters.query.all()
        for item in db_result:
            people.append(item.serialize())
        return jsonify(people), 200
    
    return "Invalid Method", 404

@app.route('/people/<int:char_id>', methods=['GET'])
@jwt_required()
def get_people_id(char_id):
    if request.method == 'GET':
        people = []
        db_result = Characters.query.filter_by(id=char_id).all()
        for item in db_result:
            people.append(item.serialize())
        return jsonify(people), 200
    
    return "Invalid Method", 404

@app.route('/people', methods=['POST'])
@jwt_required()
def add_new_character():
    if request.method == 'POST':
        people = Characters()
        people.name = request.get_json()['name']
        people.description = request.get_json()['description']
        people.hair_color = request.get_json()['hair_color']
        people.birth_year = request.get_json()['birth_year']
        people.gender = request.get_json()['gender']
        people.skin_color = request.get_json()['skin_color']
        people.eye_color =request.get_json()['eye_color']

        db.session.add(people)
        db.session.commit()

        # Show the updated version of the characters
        characters = []
        db_result = Characters.query.all()
        for item in db_result:
            characters.append(item.serialize())
        return jsonify(characters), 200
    
    return "An error has ocurred!", 404

@app.route('/people/<int:char_id>', methods=['PUT'])
@jwt_required()
def update_character(char_id):
    if request.method == 'PUT':
        people = Characters.query.get(char_id)

        if people is None:
            return jsonify({"error": "character not found"}), 404

        people.name = request.get_json()['name']
        people.description = request.get_json()['description']
        people.hair_color = request.get_json()['hair_color']
        people.birth_year = request.get_json()['birth_year']
        people.gender = request.get_json()['gender']
        people.skin_color = request.get_json()['skin_color']
        people.eye_color = request.get_json()['eye_color']

        db.session.commit()

        # Show the updated version of the characters
        characters = []
        db_result = Characters.query.all()
        for item in db_result:
            characters.append(item.serialize())
        return jsonify(characters), 200
    
    return "An error has ocurred!", 404

@app.route('/people/<int:char_id>', methods=['DELETE'])
@jwt_required()
def delete_character(char_id):
    if request.method == 'DELETE':
        character = Characters.query.filter_by(id=char_id).first()

        db.session.delete(character)
        db.session.commit()

        # Show the updated version of the characters
        characters = []
        db_result = Characters.query.all()
        for item in db_result:
            characters.append(item.serialize())
        return jsonify(characters), 200
    
    return "Invalid Method", 404

@app.route('/favorites/people/<int:char_id>', methods=['POST'])
@jwt_required()
def add_new_favorite_character(char_id):
    if request.method == 'POST':
        favorite = Favorites()
        favorite.user_id = get_jwt_identity()
        favorite.char_id = char_id
        favorite.type = 'characters'

        db.session.add(favorite)
        db.session.commit()

        # Show the updated version of the favorites
        favorites = []
        db_result = Favorites.query.filter_by(user_id=get_jwt_identity())
        for item in db_result:
            favorites.append(item.serialize())
        return jsonify(favorites), 200
    
    return "Invalid Method", 404

@app.route('/favorites/people/<int:char_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_character(char_id):
    if request.method == 'DELETE':
        favorite = Favorites.query.filter_by(char_id=char_id, user_id=get_jwt_identity(), type='characters').first()

        db.session.delete(favorite)
        db.session.commit()

        # Show the updated version of the favorites
        favorites = []
        db_result = Favorites.query.filter_by(user_id=get_jwt_identity())
        for item in db_result:
            favorites.append(item.serialize())
        return jsonify(favorites), 200
    
    return "Invalid Method", 404


#Planets Endpoints

@app.route('/planets', methods=['GET'])
@jwt_required()
def get_planets():
    if request.method == 'GET':
        planets = []
        db_result = Planets.query.all()
        for item in db_result:
            planets.append(item.serialize())
        return jsonify(planets), 200
    
    return "Invalid Method", 404

@app.route('/planets/<int:planet_id>', methods=['GET'])
@jwt_required()
def get_planets_id(planet_id):
    if request.method == 'GET':
        planets = []
        db_result = Planets.query.filter_by(id=planet_id).all()
        for item in db_result:
            planets.append(item.serialize())
        return jsonify(planets), 200
    
    return "Invalid Method", 404

@app.route('/planets', methods=['POST'])
@jwt_required()
def add_new_planet():
    if request.method == 'POST':
        planet = Planets()
        planet.name = request.get_json()['name']
        planet.description = request.get_json()['description']
        planet.diameter = request.get_json()['diameter']
        planet.rotation_period = request.get_json()['rotation_period']
        planet.orbital_period = request.get_json()['orbital_period']
        planet.population = request.get_json()['population']
        planet.climate = request.get_json()['climate']
        planet.terrain = request.get_json()['terrain']

        db.session.add(planet)
        db.session.commit()

        # Show the updated version of the favorites
        planets = []
        db_result = Planets.query.all()
        for item in db_result:
            planets.append(item.serialize())
        return jsonify(planets), 200
    
    return "An error has ocurred!", 404

@app.route('/planets/<int:planet_id>', methods=['PUT'])
@jwt_required()
def update_planet(planet_id):
    if request.method == 'PUT':
        planet = Planets.query.get(planet_id)

        if planet is None:
            return jsonify({"error": "planet not found"}), 404

        planet.name = request.get_json()['name']
        planet.description = request.get_json()['description']
        planet.diameter = request.get_json()['diameter']
        planet.rotation_period = request.get_json()['rotation_period']
        planet.orbital_period = request.get_json()['orbital_period']
        planet.population = request.get_json()['population']
        planet.climate = request.get_json()['climate']
        planet.terrain = request.get_json()['terrain']

        db.session.commit()

        # Show the updated version of the planets
        planets = []
        db_result = Planets.query.all()
        for item in db_result:
            planets.append(item.serialize())
        return jsonify(planets), 200
    
    return "An error has ocurred!", 404

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_planet(planet_id):
    if request.method == 'DELETE':
        planet = Planets.query.filter_by(id=planet_id).first()

        db.session.delete(planet)
        db.session.commit()

        # Show the updated version of the planets
        planets = []
        db_result = Planets.query.all()
        for item in db_result:
            planets.append(item.serialize())
        return jsonify(planets), 200
    
    return "Invalid Method", 404

@app.route('/favorites/planets/<int:planet_id>', methods=['POST'])
@jwt_required()
def add_new_favorite_planet(planet_id):
    if request.method == 'POST':
        favorite = Favorites()
        favorite.user_id = get_jwt_identity()
        favorite.planet_id = planet_id
        favorite.type = 'planets'

        db.session.add(favorite)
        db.session.commit()

        # Show the updated version of the favorites
        favorites = []
        db_result = Favorites.query.filter_by(user_id=get_jwt_identity())
        for item in db_result:
            favorites.append(item.serialize())
        return jsonify(favorites), 200
    
    return "Invalid Method", 404

@app.route('/favorites/planets/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_planet(planet_id):
    if request.method == 'DELETE':
        favorite = Favorites.query.filter_by(planet_id=planet_id, user_id=get_jwt_identity(), type='planets').first()

        db.session.delete(favorite)
        db.session.commit()

        # Show the updated version of the favorites
        favorites = []
        db_result = Favorites.query.filter_by(user_id=get_jwt_identity())
        for item in db_result:
            favorites.append(item.serialize())
        return jsonify(favorites), 200
    
    return "Invalid Method", 404


#Vehicles Endpoints

@app.route('/vehicles', methods=['GET'])
@jwt_required()
def get_vehicles():
    if request.method == 'GET':
        vehicles = []
        db_result = Vehicles.query.all()
        for item in db_result:
            vehicles.append(item.serialize())
        return jsonify(vehicles), 200
    
    return "Invalid Method", 404

@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
@jwt_required()
def get_vehicles_id(vehicle_id):
    if request.method == 'GET':
        vehicles = []
        db_result = Vehicles.query.filter_by(id=vehicle_id).all()
        for item in db_result:
            vehicles.append(item.serialize())
        return jsonify(vehicles), 200
    
    return "Invalid Method", 404

@app.route('/vehicles', methods=['POST'])
@jwt_required()
def add_new_vehicle():
    if request.method == 'POST':
        vehicle = Vehicles()
        vehicle.name = request.get_json()['name']
        vehicle.description = request.get_json()['description']
        vehicle.model = request.get_json()['model']
        vehicle.vehicle_class = request.get_json()['vehicle_class']
        vehicle.manufacturer = request.get_json()['manufacturer']
        vehicle.length = request.get_json()['length']
        vehicle.crew = request.get_json()['crew']
        vehicle.cargo_capacity = request.get_json()['cargo_capacity']

        db.session.add(vehicle)
        db.session.commit()

        # Show the updated version of the favorites
        vehicles = []
        db_result = Vehicles.query.all()
        for item in db_result:
            vehicles.append(item.serialize())
        return jsonify(vehicles), 200
    
    return "An error has ocurred!", 404

@app.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
def update_vehicle(vehicle_id):
    if request.method == 'PUT':
        vehicle = Vehicles.query.get(vehicle_id)

        if vehicle is None:
            return jsonify({"error": "vehicle not found"}), 404

        vehicle.name = request.get_json()['name']
        vehicle.description = request.get_json()['description']
        vehicle.model = request.get_json()['model']
        vehicle.vehicle_class = request.get_json()['vehicle_class']
        vehicle.manufacturer = request.get_json()['manufacturer']
        vehicle.length = request.get_json()['length']
        vehicle.crew = request.get_json()['crew']
        vehicle.cargo_capacity = request.get_json()['cargo_capacity']

        db.session.commit()

        # Show the updated version of the vehicles
        vehicles = []
        db_result = Vehicles.query.all()
        for item in db_result:
            vehicles.append(item.serialize())
        return jsonify(vehicles), 200
    
    return "An error has ocurred!", 404

@app.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle(vehicle_id):
    if request.method == 'DELETE':
        vehicle = Vehicles.query.filter_by(id=vehicle_id).first()

        db.session.delete(vehicle)
        db.session.commit()

        # Show the updated version of the vehicles
        vehicles = []
        db_result = Vehicles.query.all()
        for item in db_result:
            vehicles.append(item.serialize())
        return jsonify(vehicles), 200
    
    return "Invalid Method", 404

@app.route('/favorites/vehicles/<int:vehicle_id>', methods=['POST'])
@jwt_required()
def add_new_favorite_vehicle(vehicle_id):
    if request.method == 'POST':
        favorite = Favorites()
        favorite.user_id = get_jwt_identity()
        favorite.vehicle_id = vehicle_id
        favorite.type = 'vehicles'

        db.session.add(favorite)
        db.session.commit()

        # Show the updated version of the favorites
        favorites = []
        db_result = Favorites.query.filter_by(user_id=get_jwt_identity())
        for item in db_result:
            favorites.append(item.serialize())
        return jsonify(favorites), 200
    
    return "Invalid Method", 404

@app.route('/favorites/vehicles/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_vehicle(vehicle_id):
    if request.method == 'DELETE':
        favorite = Favorites.query.filter_by(vehicle_id=vehicle_id, user_id=get_jwt_identity(), type='vehicles').first()

        db.session.delete(favorite)
        db.session.commit()

        # Show the updated version of the favorites
        favorites = []
        db_result = Favorites.query.filter_by(user_id=get_jwt_identity())
        for item in db_result:
            favorites.append(item.serialize())
        return jsonify(favorites), 200
    
    return "Invalid Method", 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
