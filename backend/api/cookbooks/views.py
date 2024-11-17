"""
api/cookbooks - A small API for managing cookbooks.
"""
from .model import Cookbook

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


# @app.route("/cookbooks/count")
def cookbooks_count():
    """GET the count of cookbooks."""
    with current_app.app_context():
        mongo = PyMongo(current_app)
        cookbook_count = mongo.db.cookbooks.count_documents({})
    return {
        "count": cookbook_count,
    }


# @app.route("/cookbooks/")
def list_cookbooks():
    """
    GET a list of cookbook cookbooks.

    The results are paginated using the `page` parameter.
    """

    page = int(request.args.get("page", 1))
    per_page = 10  # A const value.

    # For pagination, it's necessary to sort by name,
    # then skip the number of docs that earlier pages would have displayed,
    # and then to limit to the fixed page size, ``per_page``.
    with current_app.app_context():
        mongo = PyMongo(current_app)
        cursor = mongo.db.cookbooks.find().sort("key").skip(per_page * (page - 1)).limit(per_page)
        cookbook_count = mongo.db.cookbooks.count_documents({})

    links = {
        "self": {"href": url_for(".list_cookbooks", page=page, _external=True)},
        "last": {
            "href": url_for(
                ".list_cookbooks", page=(cookbook_count // per_page) + 1, _external=True
            )
        },
    }
    # Add a 'prev' link if it's not on the first page:
    if page > 1:
        links["prev"] = {
            "href": url_for(".list_cookbooks", page=page - 1, _external=True)
        }
    # Add a 'next' link if it's not on the last page:
    if page - 1 < cookbook_count // per_page:
        links["next"] = {
            "href": url_for(".list_cookbooks", page=page + 1, _external=True)
        }
    return {
        "cookbooks": [Cookbook(**doc).to_json() for doc in cursor],
        "_links": links,
    }


# @app.route("/cookbooks/", methods=["POST"])
def new_cookbook():
    raw_cookbook = request.get_json()
    raw_cookbook["date_added"] = datetime.utcnow()
    # Validate key, name, author fields exist.
    cookbook = cookbook(**raw_cookbook)
    with current_app.app_context():
        mongo = PyMongo(current_app)
        insert_result = mongo.db.cookbooks.insert_one(cookbook.to_bson())
    cookbook.id = ObjectId(str(insert_result.inserted_id))
    print(cookbook)
    return cookbook.to_json()


# @app.route("/cookbooks/<string:key>", methods=["GET"])
def get_cookbook(key):
    with current_app.app_context():
        mongo = PyMongo(current_app)
        cookbook = mongo.db.cookbooks.find_one_or_404({"key": key})
    return Cookbook(**cookbook).to_json()


# @app.route("/cookbooks/<string:key>", methods=["PUT"])
def update_cookbook(key):
    cookbook = Cookbook(**request.get_json())
    cookbook.date_updated = datetime.utcnow()
    with app.app_context:
        mongo = PyMongo(current_app)
        updated_cookbook = mongo.db.cookbooks.find_one_and_update(
            {"key": key},
            {"$set": cookbook.to_bson()},
            return_document=ReturnDocument.AFTER,
        )
    if updated_cookbook:
        return Cookbook(**updated_cookbook).to_json()
    else:
        abort(404, "cookbook not found")


# @app.route("/cookbooks/<string:key>", methods=["DELETE"])
def delete_cookbook(key):
    with current_app.app_context():
        mongo = PyMongo(current_app)
        deleted_cookbook = mongo.db.cookbooks.find_one_and_delete(
            {"key": key},
        )
    if deleted_cookbook:
        return Cookbook(**deleted_cookbook).to_json()
    else:
        abort(404, "cookbook not found")

