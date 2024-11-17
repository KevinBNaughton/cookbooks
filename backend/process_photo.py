import base64
import json
from openai import OpenAI
import os
from pathlib import Path
from pydantic import BaseModel
from pymongo import MongoClient


class IngredientList(BaseModel):
    meat: list[str]
    produce: list[str]
    seafood: list[str]
    pantry: list[str]
    dairy: list[str]
    seafood_and_meat: list[str]
    frozen: list[str]
    other: list[str]


class InstructionStep(BaseModel):
    step: str
    details: list[str]


class RecipeExtraction(BaseModel):
    name_of_dish: str
    serving_size: str
    page_number: int
    ingredients: IngredientList
    instructions: list[InstructionStep]
    note: str | None = None


# Function to encode the image
def encode_image(image_path: Path) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def process_recipe_image(
    openai_client: OpenAI,
    image_path: str,
    image_format: str | None = None,
) -> RecipeExtraction | None:
    image_path: Path = Path(image_path)
    if image_format is None:
        image_format = image_path.suffix.lower()
    # Prepare the image
    image_str_base64_encoded = encode_image(image_path)

    # Call the OpenAI API with the image data
    print(f"Calling gpt-4o-mini with image {image_path} ...")
    completion = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant that processes images of recipes and extracts recipe information. "
                    "Please extract the recipe information from the image and convert it to into the given structure."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the recipe information from this image and return it in the specified structured. For the instruction details, please keep as much or all of the original text. If there are addiitonal notes at the bottom of the page, please add to the note field.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_format};base64,{image_str_base64_encoded}"
                        },
                    },
                ],
            },
        ],
        response_format=RecipeExtraction,
    )

    # Extract and return the generated response
    return completion.choices[0].message.parsed


def process_recipes(
    openai_client: OpenAI, image_paths: list[str]
) -> list[RecipeExtraction]:
    extracted_recipes = []
    for image_path in image_paths:
        recipe = process_recipe_image(
            openai_client,
            image_path,
        )
        if recipe is not None:
            extracted_recipes.append(recipe)
    return extracted_recipes


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    from pymongo import MongoClient

    openai_client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    mongo_client = MongoClient(os.environ.get("COOKBOOKS_CONNECTION_STRING"))
    mongo_db = mongo_client.get_database(os.environ.get("COOKBOOKS_DB_NAME"))
    recipes_collection = mongo_db.get_collection(
        os.environ.get("COOKBOOKS_RECIPES_COLLECTION")
    )

    # Specify the image file path
    images_directory = "photos"
    image_file_paths = []
    for image in os.listdir(images_directory):
        if image == ".DS_Store":
            continue
        image_file_paths.append(f"{images_directory}/{image}")
    # Process the image and extract recipe information
    print(f"Images to process: {image_file_paths}")

    results = process_recipes(
        openai_client,
        image_file_paths,
    )

    for result in results:
        # Print the structured JSON output
        result_json = result.model_dump_json(indent=4)
        print(result_json)
        mongo_insertion = recipes_collection.insert_one(json.loads(result_json))
        print(
            f"Inserted extraction into MongoDB with ID: {mongo_insertion.inserted_id}"
        )
