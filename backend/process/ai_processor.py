from openai import OpenAI

from process.image_preprocessor import RecipeImage
from process.model import RecipeExtraction


def process_recipe_image(
    client: OpenAI,
    image: RecipeImage,
) -> RecipeExtraction | None:
    # Call the OpenAI API with the image data
    print(f"Calling gpt-4o-mini on image {image} ...")
    completion = client.beta.chat.completions.parse(
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
                            "url": f"data:image/{image.file_format};base64,{image.base64}"
                        },
                    },
                ],
            },
        ],
        response_format=RecipeExtraction,
    )

    # Extract and return the generated response
    return completion.choices[0].message.parsed


def create_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)
