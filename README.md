# Critique

An IMDb-style platform for rating, reviewing and discovering **movies, books and music**.

**Stack:** Python (Flask) · HTML5 / CSS / JS · PostgreSQL (planned, mock data for now)

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Open <http://localhost:5500>.

## Project layout

| Path | What it is |
| --- | --- |
| `app.py` | Flask routes: `/` (home), `/signup`, `/login`, `POST /logout` |
| `db.py` | Data layer. Returns mock data now; each function has a `TODO(db)` with its PostgreSQL query |
| `schema.sql` | PostgreSQL schema + demo data: catalogue, reviews, bookmarks, lists, follows, search, recommendation functions |
| `templates/` | Jinja templates: `base.html`, `index.html`, `signup.html`, `login.html` |
| `static/style.css` | All styles |
| `test_app.py` | Self-check: `python test_app.py` prints `ok` |

## What works

- Home page: pick of the week, top-rated movies / books / albums, latest reviews
- Sign up: server-side validation, password hashed with Werkzeug, duplicate emails rejected.
  Users are kept **in memory** until the database is connected (lost on restart).
- Log in / log out with a session cookie. Signing up logs you in.
  Set a `SECRET_KEY` environment variable to keep people logged in across restarts.

## Connecting PostgreSQL later

1. `pip install "psycopg[binary]"` and add it to `requirements.txt`
2. Create the database and run `schema.sql` (commands at the top of the file)
3. Replace each function body in `db.py` with the query in its `TODO(db)` comment.
   The return shapes already match, so `app.py` and the templates don't change.

## Not built yet

Writing reviews, search, item detail and "See all" pages, recommendations, real cover images.
