# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MongoDB setup (reads DB name from URI if present, otherwise uses 'recipe_db')
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/recipe_db")
client = MongoClient(MONGO_URI)
try:
    db = client.get_default_database()
    if db is None:
        db = client["recipe_db"]
except Exception:
    db = client["recipe_db"]

recipes_col = db.get_collection("recipes")


@app.route("/")
def index():
    """
    Render home page and supply a list of ingredient suggestions (most common first).
    """
    pipeline = [
        {"$unwind": "$ingredients"},
        {"$group": {"_id": {"$toLower": "$ingredients"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    suggestions = [r["_id"] for r in recipes_col.aggregate(pipeline)]
    return render_template("index.html", ingredients=suggestions)


@app.route("/api/recipes/search", methods=["GET"])
def search_recipes():
    """
    Search recipes by comma-separated ingredients in query string.
    Example: /api/recipes/search?ingredients=eggs,tomato&match=partial
    match: 'partial' (default) or 'exact'
    """
    raw = request.args.get("ingredients", "")
    match_type = request.args.get("match", "partial").lower()

    have = [i.strip().lower() for i in raw.split(",") if i.strip()]
    if not have:
        return jsonify({"recipes": [], "error": "No ingredients provided"}), 400

    results = []
    # simple, clear approach: fetch and filter/score in Python
    for r in recipes_col.find():
        req = [str(x).strip().lower() for x in r.get("ingredients", [])]
        if match_type == "exact":
            if set(req).issubset(set(have)):
                results.append(r)
        else:
            common = len(set(req) & set(have))
            if common > 0:
                r_copy = dict(r)  # shallow copy to attach match_count
                r_copy["match_count"] = common
                results.append(r_copy)

    if match_type != "exact":
        results.sort(key=lambda x: x.get("match_count", 0), reverse=True)

    simplified = []
    for r in results:
        simplified.append({
            "id": str(r.get("_id")),
            "title": r.get("title"),
            "ingredients": r.get("ingredients", []),
            "steps": r.get("steps", ""),
            "tags": r.get("tags", []),
            "match_count": r.get("match_count", None)
        })

    return jsonify({"recipes": simplified})


@app.route("/add", methods=["GET", "POST"])
def add_recipe():
    """
    Add a new recipe using form data (title, ingredients comma-separated, steps, tags).
    """
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        ingredients = request.form.get("ingredients", "") or ""
        steps = request.form.get("steps", "") or ""
        tags = request.form.get("tags", "") or ""

        ingredients_list = [i.strip() for i in ingredients.split(",") if i.strip()]
        tags_list = [t.strip() for t in tags.split(",") if t.strip()]

        doc = {
            "title": title,
            "ingredients": ingredients_list,
            "steps": steps,
            "tags": tags_list
        }

        recipes_col.insert_one(doc)
        return redirect(url_for("index"))

    return render_template("add_recipe.html")


@app.route("/api/recipes", methods=["GET"])
def list_recipes_api():
    """
    Return a JSON array of all recipes (id, title, ingredients).
    """
    out = []
    for r in recipes_col.find():
        out.append({
            "id": str(r["_id"]),
            "title": r.get("title"),
            "ingredients": r.get("ingredients", [])
        })
    return jsonify(out)


if __name__ == "__main__":
    # Use debug=True in development only
    app.run(debug=True, host="127.0.0.1", port=5000)
