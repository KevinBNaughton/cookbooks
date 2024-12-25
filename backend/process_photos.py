import argparse
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from process.ai_processor import create_client, process_recipe_image
from process.db import get_collection, insert_recipe, is_cookbook
from process.image_preprocessor import preprocess_images
from process.model import RecipeExtraction, RecipeImage


def main(images_directory: Path, cookbook_key: str, dry_run: bool) -> None:
    load_dotenv()
    recipes_collection = get_collection(
        os.environ.get("COOKBOOKS_CONNECTION_STRING"),
        os.environ.get("COOKBOOKS_DB_NAME"),
        os.environ.get("COOKBOOKS_RECIPES_COLLECTION"),
    )
    cookbooks_collection = get_collection(
        os.environ.get("COOKBOOKS_CONNECTION_STRING"),
        os.environ.get("COOKBOOKS_DB_NAME"),
        os.environ.get("COOKBOOKS_COOKBOOKS_COLLECTION"),
    )

    if not is_cookbook(cookbook_key, cookbooks_collection):
        raise ValueError(
            f'--cookbook-key "{cookbook_key}" is not in the MongoDB cookbooks collection'
        )
    # Preprocess images, to not process already done images for example (if image file and dir is set up correctly)
    images = preprocess_images(images_directory, cookbook_key, recipes_collection)

    if not images:
        print("No images to process...")
        return

    print("Images to process: ")
    [print(image) for image in images]

    if dry_run:
        print("--dry-run enabled. Not processes or inserting")
        return

    time.sleep(5)

    ai_client = create_client(os.environ.get("OPENAI_API_KEY"))
    for image in images:
        recipe_extraction = process_recipe_image(ai_client, image)
        if recipe_extraction is None:
            print(f"Recipe for image {image} failed ai processing")
            continue
        insert_recipe(
            recipe_extraction,
            cookbook_key,
            recipes_collection,
        )
        os.rename(
            image.filepath,
            image.filepath.parent
            / Path(
                f"{cookbook_key}-{recipe_extraction.page_number}{image.filepath.suffix}"
            ),
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Program to process recipe images from a directory for a cookbook."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="If set, script will only print actions without AI client usage.",
    )
    parser.add_argument(
        "--images-dir",
        type=str,
        required=True,
        help="The directory where images are stored.",
    )
    parser.add_argument(
        "--cookbook-key",
        type=str,
        required=True,
        help="The cookbooks key in MongoDB.",
    )
    return parser.parse_args()


# Add command line arguments
if __name__ == "__main__":
    args = parse_args()
    main(Path(args.images_dir), args.cookbook_key, args.dry_run)
