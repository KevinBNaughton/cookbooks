import base64
import os
from pathlib import Path

from process.db import does_recipe_exist
from process.model import RecipeImage


# Encode the image as base64
def encode_image(image_path: Path) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def internal_preprocess_image(
    image_path: Path,
    cookbook_key: str,
) -> RecipeImage | None:
    image = RecipeImage(image_path, cookbook_key, image_path.suffix.lower())
    image.base64 = encode_image(image_path)
    return image


# Preprocess and don't process images to save money on AI calls.
def preprocess_images(
    images_directory: Path, cookbook_key: str, db_coll
) -> list[RecipeImage]:
    images: list[RecipeImage] = []
    for image_filename in os.listdir(images_directory):
        if image_filename == ".DS_Store":
            continue
        image_path = images_directory / Path(image_filename)
        # Check if image is already in coll
        tmp = image_path.name.split("-")
        if len(tmp) >= 2:
            page_number_str = tmp[1].split(".")[0]
            if page_number_str.isdigit() and does_recipe_exist(
                cookbook_key, int(page_number_str), db_coll
            ):
                # TODO - There can be multiple recipes on a single page...
                # File name format: `cookbook_key-PAGE_NUMBER`
                print(f"Image may already exist in db_coll: {image_path}")
                continue

        image = internal_preprocess_image(image_path, cookbook_key)
        if image is None:
            print(
                f"Error: image: {images_directory / Path(image_path)} was not processed"
            )
        images.append(image)
    return images
