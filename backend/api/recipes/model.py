# FastAPI's jsonable_encoder handles converting various non-JSON types,
# such as datetime between JSON types and native Python types.
from fastapi.encoders import jsonable_encoder

# Pydantic, and Python's built-in typing are used to define a schema
# that defines the structure and types of the different objects stored
# in the recipes collection, and managed by this API.
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict


BaseModel.model_config["json_encoders"] = {ObjectId: lambda v: str(v)}


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


class Recipe(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: ObjectId = Field(None, alias="_id")
    cookbook_key: str

    name_of_dish: str
    serving_size: str
    page_number: int
    ingredients: IngredientList
    instructions: list[InstructionStep]
    note: str | None = None

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
