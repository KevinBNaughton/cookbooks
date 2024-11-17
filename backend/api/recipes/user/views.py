"""
api/recipes/user - A small API for managing user recipes.
"""

from api.recipes.model import Recipe
from .model import UserRecipe, UserRecipeStatus

from datetime import datetime
from bson import ObjectId
from flask import abort
from flask import current_app
from flask import request
from flask import url_for
from flask import jsonify
from flask import current_app
from flask_pymongo import PyMongo
from pymongo.collection import ReturnDocument
from pymongo.collection import Collection
from flask_jwt_extended import jwt_required, get_jwt_identity


# @app.route("/recipes/user/count")
@jwt_required()
def user_recipes_count():
    """GET the total count of a user's recipes."""
    current_user_id = get_jwt_identity()
    search_dict = {"user_id": current_user_id}
    with current_app.app_context():
        mongo = PyMongo(current_app)
        recipes_count = mongo.db.user_recipes.count_documents(search_dict)
    return {
        "count": recipes_count,
    }


# @app.route("/recipes/user/")
@jwt_required()
def list_user_recipes():
    """
    GET a list of your user recipes.

    The results are paginated using the `page` parameter.
    """
    current_user_id = get_jwt_identity()
    search_dict = {"user_id": current_user_id}

    page = int(request.args.get("page", 1))
    per_page = 30  # A const value.
    cookbook_key = request.args.get("cookbook", None)
    if cookbook_key is not None:
        search_dict["cookbook_key"] = cookbook_key
    # For pagination, it's necessary to sort by name,
    # then skip the number of docs that earlier pages would have displayed,
    # and then to limit to the fixed page size, ``per_page``.
    with current_app.app_context():
        mongo = PyMongo(current_app)
        cursor = (
            mongo.db.user_recipes.find(search_dict)
            .sort("key")
            .skip(per_page * (page - 1))
            .limit(per_page)
        )
        user_recipes_count = mongo.db.user_recipes.count_documents(search_dict)

    links = {
        "self": {"href": url_for(".list_user_recipes", page=page, _external=True)},
        "last": {
            "href": url_for(
                ".list_user_recipes",
                page=(user_recipes_count // per_page) + 1,
                _external=True,
            )
        },
    }
    # Add a 'prev' link if it's not on the first page:
    if page > 1:
        links["prev"] = {
            "href": url_for(".list_user_recipes", page=page - 1, _external=True)
        }
    # Add a 'next' link if it's not on the last page:
    if page - 1 < recipes_count // per_page:
        links["next"] = {
            "href": url_for(".list_user_recipes", page=page + 1, _external=True)
        }
    return {
        "user_recipes": [UserRecipe(**doc).to_json() for doc in cursor],
        "_links": links,
    }


# @app.route("/recipes/user", methods=["POST"])
@jwt_required()
def new_user_recipe():
    current_user_id = get_jwt_identity()
    raw_user_recipe = request.get_json()
    now = datetime.utcnow()
    raw_user_recipe["created_at"] = now
    raw_user_recipe["updated_at"] = now
    raw_user_recipe["user_id"] = current_user_id
    # Validate fields exist.
    user_recipe = UserRecipe(**raw_user_recipe)
    search_dict = {
        "user_id": user_recipe.user_id,
        "recipe_id": user_recipe.recipe_id,
    }
    with current_app.app_context():
        mongo = PyMongo(current_app)
        user_recipes: MongoCollection[UserRecipe] = mongo.db.user_recipes
        if user_recipes.find_one(search_dict) is not None:
            flask.abort(400, "User Recipe already exists.")
        insert_result = user_recipes.insert_one(user_recipe.to_bson())
    user_recipe.id = ObjectId(str(insert_result.inserted_id))
    print(user_recipe)
    return user_recipe.to_json()


# @app.route("/recipes/user/<string:recipe_id>", methods=["GET"])
@jwt_required()
def get_or_create_user_recipe(recipe_id):
    current_user_id = get_jwt_identity()
    search_dict = {
        "user_id": current_user_id,
        "recipe_id": recipe_id,
    }
    with current_app.app_context():
        mongo = PyMongo(current_app)
        user_recipe = mongo.db.user_recipes.find_one(search_dict)
        if user_recipe is not None:
            return UserRecipe(**user_recipe).to_json()
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        if "cookbook_key" not in recipe:
            flask.abort(400, "cookbook_key not in recipe.")
        cookbook_key = recipe["cookbook_key"]
        user_recipe = {}
        now = datetime.utcnow()
        user_recipe["created_at"] = now
        user_recipe["updated_at"] = now
        user_recipe["user_id"] = current_user_id
        user_recipe["recipe_id"] = recipe_id
        user_recipe["cookbook_key"] = cookbook_key
        user_recipe["status"] = UserRecipeStatus.uncooked
        user_recipe = UserRecipe(**user_recipe)
        insert_result = mongo.db.user_recipes.insert_one(user_recipe.to_bson())
        user_recipe.id = ObjectId(str(insert_result.inserted_id))
        print(user_recipe)
        return user_recipe.to_json(), 201


# @app.route("/recipes/user/<string:recipe_id>", methods=["PUT"])
@jwt_required()
def update_user_recipe(recipe_id):
    current_user_id = get_jwt_identity()
    user_recipe_raw = request.get_json()
    user_recipe_raw["updated_at"] = datetime.utcnow()
    with current_app.app_context():
        mongo = PyMongo(current_app)
        updated_user_recipe = mongo.db.user_recipes.find_one_and_update(
            {"user_id": current_user_id, "recipe_id": recipe_id},
            {"$set": user_recipe_raw},
            return_document=ReturnDocument.AFTER,
        )
    if updated_user_recipe:
        return UserRecipe(**updated_user_recipe).to_json()
    else:
        flask.abort(404, "User Recipe not found")


# @app.route("/recipes/user/<string:recipe_id>", methods=["DELETE"])
@jwt_required()
def delete_user_recipe(recipe_id):
    current_user_id = get_jwt_identity()
    with current_app.app_context():
        mongo = PyMongo(current_app)
        deleted_user_recipe = mongo.db.user_recipes.find_one_and_delete(
            {"user_id": current_user_id, "recipe_id": recipe_id},
        )
    if deleted_user_recipe:
        return UserRecipe(**deleted_user_recipe).to_json()
    else:
        flask.abort(404, "User Recipe not found")
