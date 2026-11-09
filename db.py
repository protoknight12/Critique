"""Data access layer.

Every function returns what its PostgreSQL query will return (dicts with schema.sql column
names), so wiring in the database only changes this file. Each TODO(db) shows the query.
"""
from datetime import datetime

ITEMS = [
    {"id": 1, "type": "movie", "title": "Dune: Part Two", "creator": "Denis Villeneuve", "year": 2024, "genre": "Sci-Fi",
     "color1": "#c9813f", "color2": "#3b1d0e", "featured": True, "rating": 4.6, "rating_count": 142000,
     "description": "Paul Atreides unites with the Fremen on a path of revenge against the conspirators who destroyed his family."},
    {"id": 2, "type": "movie", "title": "Oppenheimer", "creator": "Christopher Nolan", "year": 2023, "genre": "Drama",
     "color1": "#2a4c91", "color2": "#0d1530", "rating": 4.4, "rating_count": 98000},
    {"id": 3, "type": "movie", "title": "Past Lives", "creator": "Celine Song", "year": 2023, "genre": "Romance",
     "color1": "#d14f8a", "color2": "#3a0f2a", "rating": 4.2, "rating_count": 31000},
    {"id": 4, "type": "movie", "title": "Perfect Days", "creator": "Wim Wenders", "year": 2023, "genre": "Drama",
     "color1": "#4c9a7a", "color2": "#0e2a22", "rating": 4.2, "rating_count": 12000},
    {"id": 5, "type": "movie", "title": "Poor Things", "creator": "Yorgos Lanthimos", "year": 2023, "genre": "Comedy",
     "color1": "#6339a4", "color2": "#170c2b", "rating": 4.1, "rating_count": 54000},
    {"id": 6, "type": "movie", "title": "Anatomy of a Fall", "creator": "Justine Triet", "year": 2023, "genre": "Thriller",
     "color1": "#a8432f", "color2": "#2a0e0a", "rating": 4.0, "rating_count": 27000},
    {"id": 7, "type": "book", "title": "Project Hail Mary", "creator": "Andy Weir", "year": 2021, "genre": "Sci-Fi",
     "color1": "#b7a0ff", "color2": "#2b2150", "rating": 4.5, "rating_count": 64000},
    {"id": 8, "type": "book", "title": "Tomorrow, and Tomorrow, and Tomorrow", "creator": "Gabrielle Zevin", "year": 2022,
     "genre": "Fiction", "color1": "#d8a44a", "color2": "#3a2608", "rating": 4.2, "rating_count": 41000},
    {"id": 9, "type": "book", "title": "Piranesi", "creator": "Susanna Clarke", "year": 2020, "genre": "Fantasy",
     "color1": "#3f7bb5", "color2": "#0b1d33", "rating": 4.3, "rating_count": 38000},
    {"id": 10, "type": "book", "title": "Circe", "creator": "Madeline Miller", "year": 2018, "genre": "Myth",
     "color1": "#872f67", "color2": "#22091a", "rating": 4.3, "rating_count": 52000},
    {"id": 11, "type": "book", "title": "The Overstory", "creator": "Richard Powers", "year": 2018, "genre": "Fiction",
     "color1": "#5d8a4a", "color2": "#142410", "rating": 4.1, "rating_count": 19000},
    {"id": 12, "type": "music", "title": "Blonde", "creator": "Frank Ocean", "year": 2016, "genre": "R&B",
     "color1": "#9b9aff", "color2": "#1a1a4a", "rating": 4.6, "rating_count": 47000},
    {"id": 13, "type": "music", "title": "To Pimp a Butterfly", "creator": "Kendrick Lamar", "year": 2015, "genre": "Hip-Hop",
     "color1": "#e06c4c", "color2": "#3a120a", "rating": 4.7, "rating_count": 51000},
    {"id": 14, "type": "music", "title": "In Rainbows", "creator": "Radiohead", "year": 2007, "genre": "Alt Rock",
     "color1": "#4cb5c9", "color2": "#0b2a30", "rating": 4.5, "rating_count": 45000},
    {"id": 15, "type": "music", "title": "Brat", "creator": "Charli XCX", "year": 2024, "genre": "Pop",
     "color1": "#c4a5ff", "color2": "#2a1a45", "rating": 4.3, "rating_count": 22000},
    {"id": 16, "type": "music", "title": "Rumours", "creator": "Fleetwood Mac", "year": 1977, "genre": "Rock",
     "color1": "#b58a3f", "color2": "#2a1d08", "rating": 4.5, "rating_count": 39000},
]

# user_id None = seeded demo review (no account). Ratings in ITEMS are the seed baseline;
# reviews added by users are blended in by _with_stats().
REVIEWS = [
    {"id": 1, "user_id": None, "name": "Maya K.", "item_id": 3, "rating": 5, "created_at": datetime(2026, 10, 2),
     "body": "Quiet, aching and devastatingly honest. The final walk to the taxi says more than any monologue could."},
    {"id": 2, "user_id": None, "name": "Jonah R.", "item_id": 9, "rating": 4, "created_at": datetime(2026, 10, 9),
     "body": "A strange, gentle labyrinth of a novel. Slow at first, then impossible to put down."},
    {"id": 3, "user_id": None, "name": "Sofia L.", "item_id": 14, "rating": 5, "created_at": datetime(2026, 10, 16),
     "body": 'Seventeen years later and "Reckoner" still sounds like it came from the future.'},
]
_next_review_id = 4

# review_id -> {user_id: 1 (like) | -1 (dislike)}
_reactions = {}
# (user_id, item_id) -> time bookmarked
_bookmarks = {}

# ponytail: in-memory until PostgreSQL is wired in; signups are lost on restart.
_users = []

# TODO(db): every item query selects ratings computed from reviews:
#   SELECT i.*, ROUND(AVG(r.rating), 1)::float AS rating, COUNT(r.id) AS rating_count
#   FROM items i LEFT JOIN reviews r ON r.item_id = i.id ... GROUP BY i.id


def _with_stats(item):
    """Copy of item with rating/rating_count blended from the seed baseline + user reviews."""
    mine = [r["rating"] for r in REVIEWS if r["item_id"] == item["id"] and r["user_id"] is not None]
    count = item["rating_count"] + len(mine)
    rating = (item["rating"] * item["rating_count"] + sum(mine)) / count
    return {**item, "rating": round(rating, 1), "rating_count": count}


def get_featured():
    # TODO(db): <item select> WHERE i.featured GROUP BY i.id LIMIT 1
    return next((_with_stats(item) for item in ITEMS if item.get("featured")), None)


def get_item(item_id):
    # TODO(db): <item select> WHERE i.id = %s GROUP BY i.id
    item = next((item for item in ITEMS if item["id"] == item_id), None)
    return _with_stats(item) if item else None


def list_items(item_type, sort="rating"):
    """All items of a type. sort: rating | year | title."""
    # TODO(db): <item select> WHERE i.type = %s GROUP BY i.id ORDER BY <sort>
    items = [_with_stats(item) for item in ITEMS if item["type"] == item_type]
    if sort == "year":
        return sorted(items, key=lambda i: i["year"], reverse=True)
    if sort == "title":
        return sorted(items, key=lambda i: i["title"].lower())
    return sorted(items, key=lambda i: (i["rating"], i["rating_count"]), reverse=True)


def get_top_rated(item_type, limit=5):
    return list_items(item_type)[:limit]


def _review_row(review, user_id=None):
    """Review plus like/dislike counts and the viewing user's own reaction."""
    reactions = _reactions.get(review["id"], {})
    return {
        **review,
        "likes": sum(1 for v in reactions.values() if v == 1),
        "dislikes": sum(1 for v in reactions.values() if v == -1),
        "my_reaction": reactions.get(user_id) if user_id else None,
    }


def get_latest_reviews(limit=3):
    # TODO(db): SELECT r.id, r.rating, r.body, r.created_at, u.name, i.id AS item_id, i.title, i.type
    #           FROM reviews r JOIN users u ON u.id = r.user_id JOIN items i ON i.id = r.item_id
    #           WHERE r.body IS NOT NULL ORDER BY r.created_at DESC LIMIT %s
    rows = sorted((r for r in REVIEWS if r["body"]), key=lambda r: r["created_at"], reverse=True)[:limit]
    return [{**r, "title": get_item(r["item_id"])["title"], "type": get_item(r["item_id"])["type"]} for r in rows]


def get_item_reviews(item_id, user_id=None):
    """Written reviews for an item, newest first, with reaction counts."""
    # TODO(db): SELECT r.*, u.name,
    #             COUNT(*) FILTER (WHERE x.value = 1) AS likes, COUNT(*) FILTER (WHERE x.value = -1) AS dislikes,
    #             MAX(x.value) FILTER (WHERE x.user_id = %s) AS my_reaction
    #           FROM reviews r JOIN users u ON u.id = r.user_id
    #           LEFT JOIN review_reactions x ON x.review_id = r.id
    #           WHERE r.item_id = %s AND r.body IS NOT NULL GROUP BY r.id, u.name ORDER BY r.created_at DESC
    rows = [r for r in REVIEWS if r["item_id"] == item_id and r["body"]]
    return [_review_row(r, user_id) for r in sorted(rows, key=lambda r: r["created_at"], reverse=True)]


def get_user_review(user_id, item_id):
    # TODO(db): SELECT * FROM reviews WHERE user_id = %s AND item_id = %s
    return next((r for r in REVIEWS if r["user_id"] == user_id and r["item_id"] == item_id), None)


def get_review(review_id):
    # TODO(db): SELECT * FROM reviews WHERE id = %s
    return next((r for r in REVIEWS if r["id"] == review_id), None)


def save_review(user_id, user_name, item_id, rating, body):
    """Create or replace the user's review of an item (one per user per item). body may be None."""
    # TODO(db): INSERT INTO reviews (user_id, item_id, rating, body) VALUES (%s, %s, %s, %s)
    #           ON CONFLICT (user_id, item_id) DO UPDATE SET rating = EXCLUDED.rating, body = EXCLUDED.body
    global _next_review_id
    existing = get_user_review(user_id, item_id)
    if existing:
        existing.update(rating=rating, body=body, name=user_name)
        return existing
    review = {"id": _next_review_id, "user_id": user_id, "name": user_name, "item_id": item_id,
              "rating": rating, "body": body, "created_at": datetime.now()}
    _next_review_id += 1
    REVIEWS.append(review)
    return review


def delete_review(review_id):
    # TODO(db): DELETE FROM reviews WHERE id = %s   (review_reactions cascade)
    REVIEWS[:] = [r for r in REVIEWS if r["id"] != review_id]
    _reactions.pop(review_id, None)


def react_to_review(review_id, user_id, value):
    """value is 1 (like) or -1 (dislike). Repeating the same value removes the reaction."""
    # TODO(db): same value already stored: DELETE FROM review_reactions WHERE review_id = %s AND user_id = %s
    #           otherwise INSERT ... ON CONFLICT (review_id, user_id) DO UPDATE SET value = EXCLUDED.value
    reactions = _reactions.setdefault(review_id, {})
    if reactions.get(user_id) == value:
        del reactions[user_id]
    else:
        reactions[user_id] = value


def is_bookmarked(user_id, item_id):
    # TODO(db): SELECT EXISTS (SELECT 1 FROM bookmarks WHERE user_id = %s AND item_id = %s)
    return (user_id, item_id) in _bookmarks


def toggle_bookmark(user_id, item_id):
    """Returns True if the item is now bookmarked."""
    # TODO(db): DELETE FROM bookmarks WHERE user_id = %s AND item_id = %s RETURNING 1;
    #           if nothing was deleted: INSERT INTO bookmarks (user_id, item_id) VALUES (%s, %s)
    if (user_id, item_id) in _bookmarks:
        del _bookmarks[(user_id, item_id)]
        return False
    _bookmarks[(user_id, item_id)] = datetime.now()
    return True


def get_bookmarks(user_id):
    """The user's bookmarked items, most recently added first."""
    # TODO(db): <item select> JOIN bookmarks b ON b.item_id = i.id WHERE b.user_id = %s
    #           GROUP BY i.id, b.created_at ORDER BY b.created_at DESC
    keys = sorted((k for k in _bookmarks if k[0] == user_id), key=_bookmarks.get, reverse=True)
    return [get_item(item_id) for _, item_id in keys]


def get_user_by_email(email):
    # TODO(db): SELECT * FROM users WHERE lower(email) = lower(%s)
    return next((user for user in _users if user["email"].lower() == email.lower()), None)


def create_user(name, email, password_hash):
    """Returns the new user, or None if the email is already registered (case-insensitive)."""
    # TODO(db): INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING *
    #           and return None on psycopg.errors.UniqueViolation.
    if get_user_by_email(email):
        return None
    user = {"id": len(_users) + 1, "name": name, "email": email, "password_hash": password_hash}
    _users.append(user)
    return user
