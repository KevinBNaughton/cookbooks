"""
api/recipes - A small API for managing recipes.
"""

from datetime import datetime

from bson import ObjectId
from flask import abort, current_app, jsonify, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_pymongo import PyMongo
from pymongo.collection import ReturnDocument

from api.recipes.model import Recipe
from api.users.model import UserRecipe


# @app.route("/recipes/count")
def recipes_count():
    """GET the total count of queried recipes."""
    query = request.args.get("query", "")
    search_dict = {}
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
    search_dict = {"$sample": {"size": int(count)}}
    with current_app.app_context():
        mongo = PyMongo(current_app)
        cursor = mongo.db.recipes.aggregate([search_dict])
    recipes = [Recipe(**doc).to_json() for doc in cursor]
    for recipe in recipes:
        if "instructions" in recipe:
            del recipe["instructions"]
        if "note" in recipe:
            del recipe["note"]
    current_user_id = get_jwt_identity()
    if current_user_id is None:
        return {"recipes": recipes}

    with current_app.app_context():
        mongo = PyMongo(current_app)
        ids = [ObjectId(recipe["_id"]) for recipe in recipes]
        print(ids)
        search_agg = []
        search_agg.append({"$match": {"_id": ObjectId(current_user_id)}})
        search_agg.append({"$unwind": "$recipes"})
        # search_agg.append({"recipes": {"$elemMatch": {"recipe_id": ids}}})
        search_agg.append({"$group": {"_id": "$_id", "recipes": {"$push": "$recipes"}}})
        search_agg.append(
            {
                "$project": {
                    "recipes": {
                        "$filter": {
                            "input": "$recipes",
                            "as": "recipe",
                            "cond": {"$in": ["$$recipe.recipe_id", ids]},
                        }
                    }
                }
            }
        )
        cursor = mongo.db.users.aggregate(search_agg)
        user_recipe_map = {}
        for doc in cursor:
            for raw in doc.get("recipes", []):
                raw["recipe_id"] = ObjectId(raw["recipe_id"])
                user_recipe = UserRecipe(**raw)
                user_recipe_map[str(user_recipe.recipe_id)] = user_recipe
        for i in range(len(recipes)):
            if recipes[i]["_id"] in user_recipe_map:
                recipes[i]["user_recipe"] = user_recipe_map[recipes[i]["_id"]].to_json()
        return {"recipes": recipes}


# @app.route("/api/recipes/")
@jwt_required(optional=True)
def list_recipes():
    """
    GET a list of recipes.

    The results are paginated using the `page` parameter.
    """
    page = int(request.args.get("page", 1))
    per_page = 30  # A const value.
    cookbook_key = request.args.get("cookbook", "")
    query = request.args.get("query", "")
    user_status = request.args.get("status", "")

    # For pagination, it's necessary to sort by name,
    # then skip the number of docs that earlier pages would have displayed,
    # and then to limit to the fixed page size, ``per_page``.
    with current_app.app_context():
        mongo = PyMongo(current_app)
        search_dict = {}
        if query:
            search_dict["$text"] = {"$search": query}
        if cookbook_key:
            search_dict["cookbook_key"] = cookbook_key
        cursor = (
            mongo.db.recipes.find(search_dict)
            .sort("key")
            .skip(per_page * (page - 1))
            .limit(per_page)
        )
        recipes_count = mongo.db.recipes.count_documents(search_dict)
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
    recipes = [Recipe(**doc).to_json() for doc in cursor]
    current_user_id = get_jwt_identity()
    if current_user_id is not None:
        with current_app.app_context():
            mongo = PyMongo(current_app)
            ids = [recipe["_id"] for recipe in recipes]
            search_agg = []
            search_agg.append({"$match": {"_id": ObjectId(current_user_id)}})
            search_agg.append({"$unwind": "$recipes"})
            search_agg.append(
                {"$group": {"_id": "$_id", "recipes": {"$push": "$recipes"}}}
            )
            cursor = mongo.db.users.aggregate(search_agg)
            user_recipe_map = {}
            for doc in cursor:
                for raw in doc.get("recipes", []):
                    raw["recipe_id"] = ObjectId(raw["recipe_id"])
                    user_recipe = UserRecipe(**raw)
                    user_recipe_map[str(user_recipe.recipe_id)] = user_recipe
            for i in range(len(recipes)):
                if recipes[i]["_id"] in user_recipe_map:
                    recipes[i]["user_recipe"] = user_recipe_map[
                        recipes[i]["_id"]
                    ].to_json()

    for recipe in recipes:
        del recipe["instructions"]
        if "note" in recipe:
            del recipe["note"]
    if user_status == "cooked!":
        recipes = [
            recipe
            for recipe in recipes
            if "user_recipe" in recipe and recipe["user_recipe"]["status"] == "cooked!"
        ]
    elif user_status == "uncooked":
        recipes = [
            recipe
            for recipe in recipes
            if "user_recipe" not in recipe
            or recipe["user_recipe"]["status"] == "uncooked"
        ]
    return {
        "recipes": recipes,
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
