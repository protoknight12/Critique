"""Critique: Flask app. Run: python app.py"""
import os
import secrets

from functools import wraps

from flask import Flask, abort, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import db

app = Flask(__name__)
# ponytail: random fallback logs everyone out on restart; set SECRET_KEY in production.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # blocks cross-site POSTs (CSRF) on the cookie-authenticated forms
app.jinja_env.globals["TYPE_LABELS"] = {"movie": "Movie", "book": "Book", "music": "Album"}
# URL section <-> item type
SECTIONS = {"movies": "movie", "books": "book", "music": "music"}
SECTION_OF = {t: s for s, t in SECTIONS.items()}
SECTION_TITLES = {"movies": "Movies", "books": "Books", "music": "Albums"}
SORTS = {"rating": "Top rated", "year": "Newest", "title": "A to Z"}
MAX_REVIEW_LENGTH = 5000


@app.template_filter()
def compact(n):
    """142000 -> 142K, 2100000 -> 2.1M"""
    for size, suffix in ((1_000_000, "M"), (1_000, "K")):
        if n >= size:
            return f"{n / size:.1f}".removesuffix(".0") + suffix
    return str(n)


@app.template_filter()
def stars(rating):
    full = round(rating or 0)
    return "★" * full + "☆" * (5 - full)


@app.template_filter()
def date(value):
    return value.strftime("%b %d, %Y").replace(" 0", " ")


@app.route("/")
def index():
    return render_template(
        "index.html",
        featured=db.get_featured(),
        rows=[
            ("movies", "Top Rated Movies", db.get_top_rated("movie")),
            ("books", "Top Rated Books", db.get_top_rated("book")),
            ("music", "Top Rated Albums", db.get_top_rated("music")),
        ],
        reviews=db.get_latest_reviews(),
    )


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def item_url(item, anchor=""):
    return url_for("item_page", section=SECTION_OF[item["type"]], item_id=item["id"]) + anchor


app.jinja_env.globals["item_url"] = item_url


def safe_next(default):
    """Redirect target from the form's `next` field; only same-site paths are allowed."""
    target = request.form.get("next", "")
    ok = target.startswith("/") and not target.startswith("//") and "\\" not in target
    return target if ok else default


@app.route("/<any(movies,books,music):section>")
def browse(section):
    sort = request.args.get("sort", "rating")
    if sort not in SORTS:
        sort = "rating"
    return render_template(
        "browse.html", section=section, heading=SECTION_TITLES[section], sort=sort, sorts=SORTS,
        items=db.list_items(SECTIONS[section], sort),
    )


@app.route("/<any(movies,books,music):section>/<int:item_id>")
def item_page(section, item_id):
    item = db.get_item(item_id)
    if not item or SECTION_OF[item["type"]] != section:
        abort(404)
    user = session.get("user")
    uid = user["id"] if user else None
    return render_template(
        "item.html", item=item, section=section,
        reviews=db.get_item_reviews(item_id, uid),
        my_review=db.get_user_review(uid, item_id) if uid else None,
        bookmarked=db.is_bookmarked(uid, item_id) if uid else False,
        max_length=MAX_REVIEW_LENGTH,
    )


@app.post("/items/<int:item_id>/bookmark")
@login_required
def bookmark(item_id):
    item = db.get_item(item_id) or abort(404)
    db.toggle_bookmark(session["user"]["id"], item_id)
    return redirect(safe_next(item_url(item)))


@app.route("/bookmarks")
@login_required
def bookmarks():
    return render_template("bookmarks.html", items=db.get_bookmarks(session["user"]["id"]))


@app.post("/items/<int:item_id>/review")
@login_required
def write_review(item_id):
    item = db.get_item(item_id) or abort(404)
    rating = request.form.get("rating", "")
    body = request.form.get("body", "").strip()
    if rating not in {"1", "2", "3", "4", "5"} or len(body) > MAX_REVIEW_LENGTH:
        abort(400)
    user = session["user"]
    db.save_review(user["id"], user["name"], item_id, int(rating), body or None)
    return redirect(item_url(item, "#reviews"))


@app.post("/reviews/<int:review_id>/delete")
@login_required
def delete_review(review_id):
    review = db.get_review(review_id) or abort(404)
    if review["user_id"] != session["user"]["id"]:
        abort(403)
    item = db.get_item(review["item_id"])
    db.delete_review(review_id)
    return redirect(item_url(item, "#reviews"))


@app.post("/reviews/<int:review_id>/react")
@login_required
def react(review_id):
    review = db.get_review(review_id) or abort(404)
    value = {"like": 1, "dislike": -1}.get(request.form.get("value"))
    if value is None:
        abort(400)
    db.react_to_review(review_id, session["user"]["id"], value)
    return redirect(item_url(db.get_item(review["item_id"]), f"#review-{review_id}"))


def validate_signup(name, email, password):
    if not 1 <= len(name) <= 100:
        return "Name must be 1-100 characters."
    if "@" not in email or len(email) > 254:
        return "Enter a valid email address."
    if not 8 <= len(password) <= 1024:
        return "Password must be at least 8 characters."
    return None


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", form={})

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    error = validate_signup(name, email, password)
    user = None if error else db.create_user(name, email, generate_password_hash(password))
    if not error and not user:
        error = "An account with that email already exists."
    if error:
        return render_template("signup.html", form=request.form, error=error), 400
    log_in(user)
    return redirect(url_for("index"))


def log_in(user):
    session.clear()  # new session on login, so an old session id can't be reused
    session["user"] = {"id": user["id"], "name": user["name"]}


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", form={})

    email = request.form.get("email", "").strip()
    user = db.get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], request.form.get("password", "")):
        return render_template("login.html", form=request.form, error="Email or password is incorrect."), 400
    log_in(user)
    return redirect(url_for("index"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5500)
