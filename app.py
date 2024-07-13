from typing import Optional, List

from flask import Flask, request, jsonify
from spectree import SpecTree, Response
from pydantic.v1 import BaseModel, Field, constr, root_validator


class Profile(BaseModel):
    name: constr(min_length=2, max_length=40)
    age: int = Field(..., gt=0, lt=150, description="user age(Human)")
    height: Optional[float] = Field(None, description="user height(Human)", alias="height_in_cm")

    class Config:
        schema_extra = {
            "example": {
                "name": "very_important_user",
                "age": 42,
            }
        }


class UserQueryModel(BaseModel):
    name: str


class Message(BaseModel):
    text: str


app = Flask(__name__)
spec = SpecTree("flask")


@app.route("/")
def home():
    return "hello"


@app.route("/api/users", methods=["POST"])
@spec.validate(
    json=Profile, resp=Response(HTTP_200=Profile, HTTP_403=None), tags=["users"]
)
def user_profile():
    """
    Create user profile

    user's name, user's age, ... (long description)
    """
    user_body = request.context.json  # Pydantic model Profile
    user_body_dict = user_body.dict()
    username = user_body_dict['name']
    return jsonify(name=username, age=user_body.age, height_in_cm=user_body.height)
    return Profile(name=username, age=user_body.age, height_in_cm=user_body.height)
    return Profile(name=username, age=user_body.age, height_in_cm=user_body.height).dict()


@app.route("/api/users", methods=["GET"])
@spec.validate(query=UserQueryModel, resp=Response(HTTP_200=Profile), tags=["users"])
def get_user():
    """
    Get user profile

    :return: user profile
    """
    query = request.context.query  # Pydantic model UserQueryModel
    query.name
    return {"name": "user", "age": 42}
    return Profile(name="user", age=42).dict()
    return Profile(name="user", age=42)


class CatQueryModel(BaseModel):
    colors: List[str]
    gender: str

    @root_validator
    def validate_colors_gender(cls, values):
        colors = values.get("colors")
        gender = values.get("gender")
        if len(colors) > 2 and not gender == "female":
            raise ValueError("Cats with three colors must be female")
        return values


@app.route("/api/cats", methods=["GET"])
@spec.validate(query=CatQueryModel, resp=Response(HTTP_200=Message), tags=["cats"])
def get_cats():
    return Message(text="meow")


if __name__ == "__main__":
    spec.register(app)
    app.run(port=8000)
