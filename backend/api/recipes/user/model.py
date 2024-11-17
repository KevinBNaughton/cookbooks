# FastAPI's jsonable_encoder handles converting various non-JSON types,
# such as datetime between JSON types and native Python types.
from fastapi.encoders import jsonable_encoder

# Pydantic, and Python's built-in typing are used to define a schema
# that defines the structure and types of the different objects stored
# in the recipes collection, and managed by this API.
from bson import ObjectId
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


BaseModel.model_config["json_encoders"] = {ObjectId: lambda v: str(v)}


class UserRecipeStatus(str, Enum):
    uncooked = "uncooked"
    cooked = "cooked!"


class UserRecipe(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: ObjectId = Field(None, alias="_id")
    cookbook_key: str
    recipe_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    status: UserRecipeStatus
    rating: int | None = None
    note: str | None = None

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
