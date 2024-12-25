# FastAPI's jsonable_encoder handles converting various non-JSON types,
# such as datetime between JSON types and native Python types.
from datetime import datetime
from enum import Enum

# Pydantic, and Python's built-in typing are used to define a schema
# that defines the structure and types of the different objects stored
# in the recipes collection, and managed by this API.
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field

BaseModel.model_config["json_encoders"] = {ObjectId: lambda v: str(v)}


class UserRecipeStatus(str, Enum):
    uncooked = "uncooked"
    cooked = "cooked!"

    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class UserRecipe(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cookbook_key: str
    recipe_id: ObjectId
    created_at: datetime
    updated_at: datetime

    status: UserRecipeStatus
    rating: int | None = None
    note: str | None = None

    # @classmethod
    # def validate_all_fields(cls, field_values):
    #     UserRecipe.validate_status(field_values["status"])
    #     if rating in field_values:
    #         UserRecipe.validate_rating(field_values["rating"])
    #     if note in field_values:
    #         UserRecipe.validate_note(field_values["note"])
    #     # print(f"{cls}: Field values are: {field_values}")
    #     return field_values

    @staticmethod
    def validate_status(status: str | None) -> bool:
        if status is None:
            return False
        if status in UserRecipeStatus:
            return True
        return False

    @staticmethod
    def validate_rating(rating: int | None) -> bool:
        if rating is None:
            return False
        if rating > 0 and rating < 11:
            return True
        return False

    @staticmethod
    def validate_note(note: str | None) -> bool:
        if note is None:
            return False
        if note:
            return True
        return False

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data


class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: ObjectId = Field(None, alias="_id")

    email: str
    password: str
    first_name: str
    last_name: str
    recipes: list[UserRecipe] = []

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
