from dataclasses import dataclass
from typing import List, Union

from flask import Flask, jsonify, request


# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
    name: str


@dataclass
class RequiredItem:
    name: str
    quantity: int


@dataclass
class Recipe(CookbookEntry):
    required_items: List[RequiredItem]


@dataclass
class Ingredient(CookbookEntry):
    cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = None


# Task 1 helper (don't touch)
@app.route("/parse", methods=["POST"])
def parse():
    data = request.get_json()
    recipe_name = data.get("input", "")
    parsed_name = parse_handwriting(recipe_name)
    if parsed_name is None:
        return "Invalid recipe name", 400
    return jsonify({"msg": parsed_name}), 200


# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that


def iswhitespace(chr: str) -> bool:
    return chr.isspace() or chr == "_" or chr == "-"


def parse_handwriting(recipeName: str) -> Union[str | None]:
    tokens = []
    str_buff = (
        recipeName[0].upper() if len(recipeName) > 0 and recipeName[0].isalpha() else ""
    )
    str_iter = iter(recipeName[1:])

    while c := next(str_iter, None):
        if c.isalpha():
            str_buff += c.lower()
        elif iswhitespace(c):
            if str_buff:
                tokens.append(str_buff)
                str_buff = ""

            # skip all whitespace
            while (c := next(str_iter, None)) and iswhitespace(c):
                pass
            if c:
                str_buff += c.upper()

    # there could be a remaining word left in the buffer
    if str_buff:
        tokens.append(str_buff)
    new_name = " ".join(tokens)
    return new_name if len(new_name) > 0 else None


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route("/entry", methods=["POST"])
def create_entry():
    # TODO: implement me
    return "not implemented", 500


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route("/summary", methods=["GET"])
def summary():
    # TODO: implement me
    return "not implemented", 500


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == "__main__":
    app.run(debug=True, port=8080)
