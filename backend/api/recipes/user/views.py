"""
api/recipes/user - A small API for managing user recipes.
"""

from datetime import datetime

from bson import ObjectId
from flask import abort, current_app, jsonify, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_pymongo import PyMongo
from pymongo.collection import Collection, ReturnDocument

from api.recipes.model import Recipe
from api.users.model import UserRecipe, UserRecipeStatus


# @app.route("/recipes/user/count")
@jwt_required()
def user_recipes_count():
    """GET the total count of a user's recipes."""
    current_user_id = get_jwt_identity()
    with current_app.app_context():
        mongo = PyMongo(current_app)
        recipes_count = mongo.db.users.aggregate(
            [
                {"$match": {"_id": ObjectId(current_user_id)}},
                {"$project": {"total_recipes": {"$size": "$recipes"}}},
            ]
        )
    return {
        "count": recipes_count["total_recipes"],
    }


# @app.route("/recipes/user/")
@jwt_required()
def list_user_recipes():
    """
    GET a list of your user recipes.

    The results are paginated using the `page` parameter.
    """
    current_user_id = get_jwt_identity()

    page = int(request.args.get("page", 1))
    per_page = 30  # A const value.
    # cookbook_key = request.args.get("cookbook", None)
    # if cookbook_key is not None:
    #     search_dict["cookbook_key"] = cookbook_key
    # For pagination, it's necessary to sort by name,
    # then skip the number of docs that earlier pages would have displayed,
    # and then to limit to the fixed page size, ``per_page``.
    with current_app.app_context():
        mongo = PyMongo(current_app)
        cursor = (
            mongo.db.users.aggregate(
                [
                    {"$match": {"_id": ObjectId(current_user_id)}},
                    {"$unwind": "$recipes"},
                    {"$sort": {"recipes.created_at": -1}},
                    {"$limit": per_page * page},
                    {"$skip": per_page * (page - 1)},
                    {"$group": {"_id": "$_id", "recipes": {"$push": "$recipes"}}},
                ]
            )
            # .sort("key")
            # .skip(per_page * (page - 1))
            # .limit(per_page)
        )
        count_cursor = mongo.db.users.aggregate(
            [
                {"$match": {"_id": ObjectId(current_user_id)}},
                {"$project": {"total_recipes": {"$size": "$recipes"}}},
            ]
        )
        for x in count_cursor:
            recipes_count = x["total_recipes"]

    links = {
        "self": {"href": url_for(".list_user_recipes", page=page, _external=True)},
        "last": {
            "href": url_for(
                ".list_user_recipes",
                page=max(1, (recipes_count // per_page)),
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
    if page < recipes_count // per_page:
        links["next"] = {
            "href": url_for(".list_user_recipes", page=page + 1, _external=True)
        }
    return {
        "user_recipes": [
            UserRecipe(**raw).to_json()
            for doc in cursor
            for raw in doc.get("recipes", [])
        ],
        "_links": links,
    }


# @app.route("/recipes/user", methods=["POST"])
@jwt_required()
def new_user_recipe():
    current_user_id = get_jwt_identity()
    raw_user_recipe = request.get_json()
    now = datetime.utcnow()

    if "status" in raw_user_recipe:
        if not UserRecipe.validate_status(raw_user_recipe["status"]):
            return f"Status '{raw_user_recipe["status"]}' is invalid", 400
    if "rating" in raw_user_recipe:
        if not UserRecipe.validate_rating(raw_user_recipe["rating"]):
            return f"Status '{raw_user_recipe["rating"]}' is invalid", 400
    if "note" in raw_user_recipe:
        if not UserRecipe.validate_note(raw_user_recipe["note"]):
            return "Note is empty", 400

    raw_user_recipe["created_at"] = now
    raw_user_recipe["updated_at"] = now
    # Validate fields exist.
    user_recipe = UserRecipe(**raw_user_recipe)
    search_dict = {
        "_id": ObjectId(current_user_id),
        "recipes.$.recipe_id": ObjectId(user_recipe.recipe_id),
    }
    with current_app.app_context():
        mongo = PyMongo(current_app)
        user_coll: MongoCollection[User] = mongo.db.users
        if user_coll.find_one(search_dict) is not None:
            abort(400, "User Recipe already exists.")
        insert_result = user_coll.find_one_and_update(
            {"_id": ObjectId(current_user_id)},
            {"$push": {"recipes": user_recipe.to_bson()}},
        )
        insert_result = user_coll.insert_one(user_recipe.to_bson())
    user_recipe.id = ObjectId(str(insert_result.inserted_id))
    return user_recipe.to_json()


# @app.route("/recipes/user/<string:recipe_id>", methods=["GET"])
@jwt_required()
def get_or_create_user_recipe(recipe_id):
    current_user_id = get_jwt_identity()
    search_user = {
        "_id": ObjectId(current_user_id),
        "recipes": {"$elemMatch": {"recipe_id": ObjectId(recipe_id)}},
    }
    with current_app.app_context():
        mongo = PyMongo(current_app)
        user_recipe_cursor = mongo.db.users.find_one(search_user, {"recipes.$": 1})
        if user_recipe_cursor is not None:
            return UserRecipe(**user_recipe_cursor["recipes"][0]).to_json(), 200
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        if "cookbook_key" not in recipe:
            abort(400, "cookbook_key not in recipe.")
        cookbook_key = recipe["cookbook_key"]
        user_recipe = {}
        now = datetime.utcnow()
        user_recipe["created_at"] = now
        user_recipe["updated_at"] = now
        user_recipe["recipe_id"] = ObjectId(recipe_id)
        user_recipe["cookbook_key"] = cookbook_key
        user_recipe["status"] = UserRecipeStatus.uncooked
        user_recipe = UserRecipe(**user_recipe)
        insert_result = mongo.db.users.find_one_and_update(
            {"_id": ObjectId(current_user_id)},
            {"$push": {"recipes": user_recipe.to_bson()}},
        )
        return user_recipe.to_json(), 201


# @app.route("/recipes/user/<string:recipe_id>", methods=["PUT"])
@jwt_required()
def update_user_recipe(recipe_id):
    # TODO validate input fields
    current_user_id = get_jwt_identity()

    user_recipe_raw = request.get_json()
    update_dict = {}
    if "status" in user_recipe_raw:
        if not UserRecipe.validate_status(user_recipe_raw["status"]):
            return f"Status '{user_recipe_raw["status"]}' is invalid", 400
        update_dict["recipes.$.status"] = user_recipe_raw["status"]
    if "rating" in user_recipe_raw:
        if not UserRecipe.validate_rating(user_recipe_raw["rating"]):
            return f"Status '{user_recipe_raw["rating"]}' is invalid", 400
        update_dict["recipes.$.rating"] = user_recipe_raw["rating"]
    if "note" in user_recipe_raw:
        if not UserRecipe.validate_note(user_recipe_raw["note"]):
            return "Note is empty", 400
        update_dict["recipes.$.note"] = user_recipe_raw["note"]
    if not update_dict:
        return "No updates requested", 400
    update_dict["recipes.$.updated_at"] = datetime.utcnow()

    with current_app.app_context():
        mongo = PyMongo(current_app)
        original_user = mongo.db.users.find_one_and_update(
            {
                "_id": ObjectId(current_user_id),
                "recipes.recipe_id": ObjectId(recipe_id),
            },
            {"$set": update_dict},
            {"recipes.$": 1},
            # return_document=ReturnDocument.AFTER,
        )
    if original_user:
        original_user_recipe = original_user["recipes"][0]
        if "status" in user_recipe_raw:
            original_user_recipe["status"] = user_recipe_raw["status"]
        if "rating" in user_recipe_raw:
            original_user_recipe["rating"] = user_recipe_raw["rating"]
        if "note" in user_recipe_raw:
            original_user_recipe["note"] = user_recipe_raw["note"]
        original_user_recipe["updated_at"] = update_dict["recipes.$.updated_at"]
        return UserRecipe(**original_user_recipe).to_json()
    else:
        abort(404, "User Recipe not found")


# @app.route("/recipes/user/<string:recipe_id>", methods=["DELETE"])
@jwt_required()
def delete_user_recipe(recipe_id):
    current_user_id = get_jwt_identity()
    with current_app.app_context():
        mongo = PyMongo(current_app)
        deleted_user_recipe = mongo.db.users.find_one_and_update(
            {
                "_id": ObjectId(current_user_id),
                "recipes.recipe_id": ObjectId(recipe_id),
            },
            {"$pull": {"recipes": {"recipe_id": ObjectId(recipe_id)}}},
            {"recipes.$": 1},
        )
    if deleted_user_recipe and "recipes" in deleted_user_recipe:
        return UserRecipe(**deleted_user_recipe["recipes"][0]).to_json()
    else:
        abort(404, "User Recipe not found")
