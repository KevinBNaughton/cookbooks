"""
api/users - A small API for managing users.
"""

from .model import User

from datetime import datetime
from bson import ObjectId
from flask import abort
from flask import current_app
from flask import request
from flask import url_for
from flask import jsonify
from flask_pymongo import PyMongo
from pymongo.collection import ReturnDocument
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


# @app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400
    with current_app.app_context():
        mongo = PyMongo(current_app)
        if mongo.db.users.find_one({"email": email}):
            return jsonify({"msg": "Email already exists"}), 409
        bcrypt = Bcrypt(current_app)
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        raw_user = {
            "email": email,
            "password": hashed_password,
            "first_name": first_name,
            "last_name": last_name,
        }
        user = User(**raw_user)
        insert_result = mongo.db.users.insert_one(user.to_bson())
        user.id = ObjectId(str(insert_result.inserted_id))
        return jsonify({"msg": "User created successfully"}), 201


# @app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400
    with current_app.app_context():
        mongo = PyMongo(current_app)
        user = mongo.db.users.find_one({"email": email})
        if not user:
            return jsonify({"msg": "Bad email or password"}), 401
        bcrypt = Bcrypt(current_app)
        if not bcrypt.check_password_hash(user["password"], password):
            return jsonify({"msg": "Bad email or password"}), 401
        # Create JWT token
        access_token = create_access_token(identity=str(user["_id"]))
        return jsonify(access_token=access_token, user=User(**user).to_json()), 200


# @app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    with current_app.app_context():
        mongo = PyMongo(current_app)
        user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            return jsonify({"msg": "User not found"}), 404
        return jsonify(logged_in_as=user["email"]), 200
    flask.abort(404, "user not found")


# @app.route("/api/users/<string:email>", methods=["GET"])
def get_user(email):
    with current_app.app_context():
        mongo = PyMongo(current_app)
        user = mongo.db.users.find_one_or_404({"email": email})
    return User(**user).to_json()


# @app.route("/api/users/<string:email>", methods=["PUT"])
def update_user(email):
    user = User(**request.get_json())
    user.date_updated = datetime.utcnow()
    with app.app_context:
        mongo = PyMongo(current_app)
        updated_user = mongo.db.users.find_one_and_update(
            {"_id": _id},
            {"$set": recipe.to_bson()},
            return_document=ReturnDocument.AFTER,
        )
    if updated_user:
        return User(**updated_user).to_json()
    else:
        flask.abort(404, "user not found")
