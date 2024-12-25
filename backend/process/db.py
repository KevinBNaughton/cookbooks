import json

from pymongo import MongoClient
from pymongo.collection import Collection

from process.model import RecipeExtraction


def insert_recipe(
    recipe: RecipeExtraction,
    cookbook_key: str,
    recipes_collection: Collection,  # TODO - Add typing
) -> None:
    recipe_json = json.loads(recipe.model_dump_json())
    recipe_json["cookbook_key"] = cookbook_key
    mongo_insertion = recipes_collection.insert_one(recipe_json)
    print(f"Inserted extraction into MongoDB with ID: {mongo_insertion.inserted_id}")


def is_cookbook(cookbook_key: str, collection: Collection) -> bool:
    # Checks if a cookbook_key exists in the cookbooks DB.
    if collection.find_one({"key": cookbook_key}) is not None:
        return True
    return False


def does_recipe_exist(
    cookbook_key: str, page_number: int, collection: Collection
) -> bool:
    if collection.find_one({"cookbook_key": cookbook_key, "page_number": page_number}):
        return True
    return False


def get_collection(client_env: str, db_env: str, collection_env: str) -> Collection:
    mongo_client = MongoClient(client_env)
    mongo_db = mongo_client.get_database(db_env)
    collection = mongo_db.get_collection(collection_env)
    return collection
