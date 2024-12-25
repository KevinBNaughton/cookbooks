import os
from typing import Any

from bson import json_util
from dotenv import load_dotenv
from flask import Flask, Response, g
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from pymongo import MongoClient

import api.cookbooks.views as cookbooks_view
import api.recipes.user.views as user_recipes_view
import api.recipes.views as recipes_view
import api.users.views as users_view

load_dotenv()


app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
jwt = JWTManager(app)
app.config.from_prefixed_env("COOKBOOKS")
app.config["MONGO_URI"] = f'{app.config["CONNECTION_STRING"]}{app.config["DB_NAME"]}'
app.url_map.strict_slashes = False


def init_mongodb_client(app: Flask):
    try:
        print(
            f"Attempting to connect to MongoDB connection string: {app.config['CONNECTION_STRING']} and DB: {app.config['DB_NAME']} ..."
        )
        mongo = PyMongo(app)
        result = mongo.db.command("ping")
        if int(result.get("ok")) == 1:
            print("Connected")
        else:
            raise Exception("Cluster ping returned OK != 1")
    except Exception as e:
        raise e


init_mongodb_client(app)

# Users and login
app.add_url_rule(
    "/api/login",
    view_func=users_view.login,
    methods=["POST"],
)
app.add_url_rule(
    "/api/signup",
    view_func=users_view.signup,
    methods=["POST"],
)
app.add_url_rule(
    "/api/users/protected",
    view_func=users_view.protected,
    methods=["GET"],
)
app.add_url_rule(
    "/api/users/token",
    view_func=users_view.check_token,
    methods=["GET"],
)
app.add_url_rule(
    "/api/users/<string:email>",
    view_func=users_view.get_user,
    methods=["GET"],
)
app.add_url_rule(
    "/api/users/<string:email>",
    view_func=users_view.update_user,
    methods=["PUT"],
)

# Cookbooks
app.add_url_rule(
    "/api/cookbooks", view_func=cookbooks_view.list_cookbooks, methods=["GET"]
)
app.add_url_rule(
    "/api/cookbooks/count", view_func=cookbooks_view.cookbooks_count, methods=["GET"]
)
app.add_url_rule(
    "/api/cookbooks/<string:key>",
    view_func=cookbooks_view.get_cookbook,
    methods=["GET"],
)
app.add_url_rule(
    "/api/cookbooks/<string:key>",
    view_func=cookbooks_view.update_cookbook,
    methods=["POST"],
)
app.add_url_rule(
    "/api/cookbooks/<string:key>",
    view_func=cookbooks_view.delete_cookbook,
    methods=["DELETE"],
)

# Recipes
app.add_url_rule("/api/recipes", view_func=recipes_view.list_recipes, methods=["GET"])
app.add_url_rule(
    "/api/recipes/count", view_func=recipes_view.recipes_count, methods=["GET"]
)
app.add_url_rule(
    "/api/recipes/random/<int:count>",
    view_func=recipes_view.get_n_random_recipes,
    methods=["GET"],
)
app.add_url_rule(
    "/api/recipes/recipe/<string:_id>",
    view_func=recipes_view.get_recipe,
    methods=["GET"],
)
app.add_url_rule(
    "/api/recipes/recipe/<string:_id>",
    view_func=recipes_view.update_recipe,
    methods=["PUT"],
)
app.add_url_rule(
    "/api/recipes/recipe/<string:_id>",
    view_func=recipes_view.delete_recipe,
    methods=["DELETE"],
)

# User Recipes
app.add_url_rule(
    "/api/recipes/user", view_func=user_recipes_view.list_user_recipes, methods=["GET"]
)
app.add_url_rule(
    "/api/recipes/user", view_func=user_recipes_view.new_user_recipe, methods=["POST"]
)
app.add_url_rule(
    "/api/recipes/user/count",
    view_func=user_recipes_view.user_recipes_count,
    methods=["GET"],
)
app.add_url_rule(
    "/api/recipes/user/<string:recipe_id>",
    view_func=user_recipes_view.get_or_create_user_recipe,
    methods=["GET"],
)
app.add_url_rule(
    "/api/recipes/user/<string:recipe_id>",
    view_func=user_recipes_view.update_user_recipe,
    methods=["PUT"],
)
app.add_url_rule(
    "/api/recipes/user/<string:recipe_id>",
    view_func=user_recipes_view.delete_user_recipe,
    methods=["DELETE"],
)
