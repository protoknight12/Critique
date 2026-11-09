"""Run: python test_app.py"""
from app import app, compact

client = app.test_client()

home = client.get("/")
assert home.status_code == 200
assert b"Dune: Part Two" in home.data and b"Top Rated Albums" in home.data

assert compact(142000) == "142K" and compact(2_100_000) == "2.1M" and compact(48) == "48"

signup = lambda email, password: client.post("/signup", data={"name": "Test User", "email": email, "password": password})
assert signup("t@example.com", "short").status_code == 400
assert signup("t@example.com", "longenough").status_code == 302
assert b"Test User" in client.get("/").data  # signup logs you in
assert signup("T@EXAMPLE.com", "longenough").status_code == 400  # duplicate, case-insensitive
assert b"already exists" in signup("t@example.com", "longenough").data

assert client.post("/logout").status_code == 302
assert b"Test User" not in client.get("/").data

login = lambda email, password: client.post("/login", data={"email": email, "password": password})
assert login("t@example.com", "wrongpassword").status_code == 400
assert login("nobody@example.com", "longenough").status_code == 400
assert login("T@example.com", "longenough").status_code == 302
assert b"Test User" in client.get("/").data

# --- browse + item pages
for path, text in (("/movies", b"Oppenheimer"), ("/books", b"Piranesi"), ("/music", b"Blonde")):
    assert text in client.get(path).data
assert client.get("/movies?sort=bogus").status_code == 200
assert client.get("/movies/1").status_code == 200 and b"Dune: Part Two" in client.get("/movies/1").data
assert client.get("/books/1").status_code == 404  # right id, wrong section
assert client.get("/movies/999").status_code == 404

# --- bookmarks (still logged in as Test User)
assert b"Nothing saved yet" in client.get("/bookmarks").data
assert client.post("/items/2/bookmark", data={"next": "/movies/2"}).headers["Location"] == "/movies/2"
assert client.post("/items/2/bookmark", data={"next": "//evil.com"}).headers["Location"] == "/movies/2"  # toggled off, safe redirect
assert b"Nothing saved yet" in client.get("/bookmarks").data
client.post("/items/2/bookmark")
assert b"Oppenheimer" in client.get("/bookmarks").data and b"Bookmarked" in client.get("/movies/2").data

# --- reviews
review = lambda item, rating, body="": client.post(f"/items/{item}/review", data={"rating": rating, "body": body})
assert review(2, "9").status_code == 400
assert review(2, "5", "x" * 5001).status_code == 400
assert review(2, "5", "<b>Great</b>").status_code == 302
page = client.get("/movies/2").data
assert b"&lt;b&gt;Great&lt;/b&gt;" in page and b"<b>Great</b>" not in page  # escaped
assert review(2, "3", "Changed my mind").status_code == 302  # replaces, doesn't add
page = client.get("/movies/2").data
assert page.count(b'class="review"') == 1 and b"Changed my mind" in page

# --- reactions: the review is Test User's, id 4; like, switch to dislike, repeat to remove
assert b"Like \xc2\xb7 0" in page
client.post("/reviews/4/react", data={"value": "like"})
assert b"Like \xc2\xb7 1" in client.get("/movies/2").data
client.post("/reviews/4/react", data={"value": "dislike"})
page = client.get("/movies/2").data
assert b"Like \xc2\xb7 0" in page and b"Dislike \xc2\xb7 1" in page
client.post("/reviews/4/react", data={"value": "dislike"})
assert b"Dislike \xc2\xb7 0" in client.get("/movies/2").data
assert client.post("/reviews/4/react", data={"value": "meh"}).status_code == 400

# --- only the author can delete; logged-out users are sent to log in
other = app.test_client()
assert other.post("/reviews/4/react", data={"value": "like"}).headers["Location"].endswith("/login")
other.post("/signup", data={"name": "Other", "email": "o@example.com", "password": "longenough"})
assert other.post("/reviews/4/delete").status_code == 403
assert client.post("/reviews/4/delete").status_code == 302
assert b"Changed my mind" not in client.get("/movies/2").data

print("ok")
