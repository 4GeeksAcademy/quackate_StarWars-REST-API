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
