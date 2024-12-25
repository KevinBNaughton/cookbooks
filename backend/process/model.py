from pathlib import Path

from pydantic import BaseModel


class RecipeImage:
    def __init__(self, filepath: Path, cookbook_key: str, file_format: str) -> None:
        self.filepath = filepath
        self.cookbook_key = cookbook_key
        self.file_format = file_format
        self.base64 = None

    def __str__(self):
        return f"RecipeImage(filepath={self.filepath}, cookbook_key={self.cookbook_key}, file_format={self.file_format})"


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
