from collections import defaultdict
from dataclasses import dataclass
from typing import List, Optional, Union

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

db: dict[str, CookbookEntry] = {}


@app.route("/entry", methods=["POST"])
def create_entry():
    data = request.get_json()
    if data["name"] in db:
        return {}, 400

    if data["type"] == "recipe":
        seen = set()
        for item in data["requiredItems"]:
            if item["name"] in seen:
                return {}, 400
            seen.add(item["name"])

        db[data["name"]] = Recipe(
            name=data["name"],
            required_items=list(
                map(
                    lambda e: RequiredItem(name=e["name"], quantity=e["quantity"]),
                    data["requiredItems"],
                )
            ),
        )
        return {}, 200

    elif data["type"] == "ingredient":
        if data["cookTime"] < 0:
            return {}, 400
        db[data["name"]] = Ingredient(name=data["name"], cook_time=data["cookTime"])
        return {}, 200

    return {}, 400


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
def get_summary(entry: CookbookEntry) -> Optional[dict]:
    ingredients = defaultdict(int)
    cook_time = 0

    def dfs(entry: CookbookEntry, quantity: int = 1) -> Optional[str]:
        nonlocal cook_time
        if isinstance(entry, Ingredient):
            cook_time += entry.cook_time * quantity
            ingredients[entry.name] += quantity
            return "OK"
        if isinstance(entry, Recipe):
            for item in entry.required_items:
                if item.name not in db:
                    return None

                if not dfs(item, item.quantity * quantity):
                    return None
        return "OK"

    if not dfs(entry):
        return None

    return {
        "name": entry.name,
        "cookTime": cook_time,
        "ingredients": [{"name": k, "quantity": v} for k, v in ingredients.items()],
    }


@app.route("/summary", methods=["GET"])
def summary():
    name = request.args.get("name")
    if name not in db or not isinstance(db[name], Recipe):
        return {}, 400
    res = get_summary(db[name])
    if not res:
        return {}, 400

    return res, 200


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == "__main__":
    app.run(debug=True, port=8080)
