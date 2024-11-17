"""
api/recipes - A small API for managing recipes.
"""

from .model import Recipe

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
from flask_jwt_extended import jwt_required, get_jwt_identity


# @app.route("/recipes/count")
def recipes_count():
    """GET the total count of all recipes."""
    with current_app.app_context():
        mongo = PyMongo(current_app)
        recipes_count = mongo.db.recipes.count_documents({})
    return {
        "count": recipes_count,
    }


# @app.route("/recipes/count/search")
def search_recipes_count():
    """GET the total count of queried recipes."""
    query = request.args.get("query", "")
    search_dict = {}
    # if cookbook_key is not None:
    # search_dict["cookbook_key"] = cookbook_key
    if query:
        search_dict["$text"] = {"$search": query}
    with current_app.app_context():
        mongo = PyMongo(current_app)
        recipes_count = mongo.db.recipes.count_documents(search_dict)
    return {
        "count": recipes_count,
    }


# @app.route("/recipes/random/<int:count>", methods=["GET"])
@jwt_required(optional=True)
def get_n_random_recipes(count):
    """
    GET n random recipes.

    The results are paginated using the `page` parameter.
    """
    # cookbook_key = request.args.get("cookbook", None)
    # query = request.args.get("query", "")
    current_user_id = get_jwt_identity()
    search_dict = {"$sample": {"size": int(count)}}
    print(f"current_user_id: {current_user_id}")
    with current_app.app_context():
        mongo = PyMongo(current_app)
        cursor = mongo.db.recipes.aggregate([search_dict])
    recipes = [Recipe(**doc).to_json() for doc in cursor]
    for recipe in recipes:
        if "instructions" in recipe:
            del recipe["instructions"]
        if "note" in recipe:
            del recipe["note"]
    return {"recipes": recipes}


# @app.route("/recipes/search")
def search_recipes():
    """
    GET Search for recipes.

    The results are paginated using the `page` parameter.
    """
    page = int(request.args.get("page", 1))
    per_page = 30  # A const value.
    cookbook_key = request.args.get("cookbook", None)
    query = request.args.get("query", "")

    # For pagination, it's necessary to sort by name,
    # then skip the number of docs that earlier pages would have displayed,
    # and then to limit to the fixed page size, ``per_page``.
    with current_app.app_context():
        mongo = PyMongo(current_app)
        search_dict = {}
        # if cookbook_key is not None:
        # search_dict["cookbook_key"] = cookbook_key
        if query:
            search_dict["$text"] = {"$search": query}
        cursor = (
            mongo.db.recipes.find(search_dict)
            .sort("key")
            .skip(per_page * (page - 1))
            .limit(per_page)
        )
        recipes_count = mongo.db.recipes.count_documents(search_dict)
    links = {
        "self": {"href": url_for(".search_recipes", page=page, _external=True)},
        "last": {
            "href": url_for(
                ".search_recipes", page=(recipes_count // per_page) + 1, _external=True
            )
        },
    }
    # Add a 'prev' link if it's not on the first page:
    if page > 1:
        links["prev"] = {
            "href": url_for(".list_recipes", page=page - 1, _external=True)
        }
    # Add a 'next' link if it's not on the last page:
    if page - 1 < recipes_count // per_page:
        links["next"] = {
            "href": url_for(".list_recipes", page=page + 1, _external=True)
        }
    return {
        "recipes": [Recipe(**doc).to_json() for doc in cursor],
        "_links": links,
    }


# @app.route("/recipes/")
def list_recipes():
    """
    GET a list of recipes.

    The results are paginated using the `page` parameter.
    """
    page = int(request.args.get("page", 1))
    per_page = 30  # A const value.
    cookbook_key = request.args.get("cookbook", None)

    # For pagination, it's necessary to sort by name,
    # then skip the number of docs that earlier pages would have displayed,
    # and then to limit to the fixed page size, ``per_page``.
    with current_app.app_context():
        mongo = PyMongo(current_app)
        if cookbook_key is not None:
            cursor = (
                mongo.db.recipes.find({"cookbook_key": cookbook_key})
                .sort("key")
                .skip(per_page * (page - 1))
                .limit(per_page)
            )
            recipes_count = mongo.db.recipes.count_documents(
                {"cookbook_key": cookbook_key}
            )
        else:
            cursor = (
                mongo.db.recipes.find()
                .sort("key")
                .skip(per_page * (page - 1))
                .limit(per_page)
            )
            recipes_count = mongo.db.recipes.count_documents({})
    links = {
        "self": {"href": url_for(".list_recipes", page=page, _external=True)},
        "last": {
            "href": url_for(
                ".list_recipes", page=(recipes_count // per_page) + 1, _external=True
            )
        },
    }
    # Add a 'prev' link if it's not on the first page:
    if page > 1:
        links["prev"] = {
            "href": url_for(".list_recipes", page=page - 1, _external=True)
        }
    # Add a 'next' link if it's not on the last page:
    if page - 1 < recipes_count // per_page:
        links["next"] = {
            "href": url_for(".list_recipes", page=page + 1, _external=True)
        }
    return {
        "recipes": [Recipe(**doc).to_json() for doc in cursor],
        "_links": links,
    }


# @app.route("/recipes/recipe", methods=["POST"])
def new_recipe():
    raw_recipe = request.get_json()
    raw_recipe["date_added"] = datetime.utcnow()
    # Validate key, name, author fields exist.
    recipe = recipe(**raw_recipe)
    with current_app.app_context():
        mongo = PyMongo(current_app)
        insert_result = mongo.db.recipes.insert_one(recipe.to_bson())
    recipe.id = ObjectId(str(insert_result.inserted_id))
    print(recipe)
    return recipe.to_json()


# @app.route("/recipes/recipe/<string:key>", methods=["GET"])
def get_recipe(_id):
    _id = ObjectId(_id)
    with current_app.app_context():
        mongo = PyMongo(current_app)
        recipe = mongo.db.recipes.find_one_or_404({"_id": _id})
    return Recipe(**recipe).to_json()


# @app.route("/recipes/recipe/<string:key>", methods=["PUT"])
def update_recipe(_id):
    _id = ObjectId(_id)
    recipe = Recipe(**request.get_json())
    recipe.date_updated = datetime.utcnow()
    with app.app_context:
        mongo = PyMongo(current_app)
        updated_recipe = mongo.db.recipes.find_one_and_update(
            {"_id": _id},
            {"$set": recipe.to_bson()},
            return_document=ReturnDocument.AFTER,
        )
    if updated_recipe:
        return Recipe(**updated_recipe).to_json()
    else:
        flask.abort(404, "recipe not found")


# @app.route("/recipes/recipe/<string:key>", methods=["DELETE"])
def delete_recipe(_id):
    _id = ObjectId(_id)
    with current_app.app_context():
        mongo = PyMongo(current_app)
        deleted_recipe = mongo.db.recipes.find_one_and_delete(
            {"_id": _id},
        )
    if deleted_recipe:
        return Recipe(**deleted_recipe).to_json()
    else:
        flask.abort(404, "recipe not found")
