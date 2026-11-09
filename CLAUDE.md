# Critique: project context

Living context for Claude. **Read this at the start of every session and update it whenever the app changes**
(new pages, routes, tables, decisions, or finished/added TODOs). Keep it short and current; history lives in git.

## What it is
IMDb-style site for rating, reviewing and getting recommendations for movies, books and music. Brand: **Critique.**
(logo `Critique<span>.</span>`), tagline "Your world of stories, sounds and cinema."

## Stack (decided by the user)
Python **Flask** · HTML5 / CSS / JS · **PostgreSQL**.
For now the user wants **basic functionality with placeholders ready for DB integration**, not a live database.
Don't wire in Postgres until asked.

## How it's built
- `app.py`: routes `/`, `/signup`, `/login`, `POST /logout`; `/movies` `/books` `/music` (browse, `?sort=rating|year|title`) and `/<section>/<id>` (item page with reviews at the bottom); `POST /items/<id>/bookmark`, `/bookmarks`; `POST /items/<id>/review`, `/reviews/<id>/delete`, `/reviews/<id>/react` (value like|dislike, repeat toggles off). Write routes use `@login_required` (redirects to login) and forms redirect via `safe_next`. Jinja filters `compact`, `stars`, `date`; global `item_url()`. Session cookie is SameSite=Lax (no CSRF tokens yet).
- `db.py`: the **only** place data comes from. Functions return dicts shaped like the PostgreSQL rows
  (column names from `schema.sql`); each has a `TODO(db)` comment with its query. DB integration = rewrite these bodies.
  Users are stored in an in-memory list for now.
- `schema.sql`: planned tables `users` (email unique case-insensitive), `items` (`type` movie/book/music, creator,
  Also `bookmarks` (user, item) and `review_reactions` (review, user, value 1/-1). In memory, item ratings = seed baseline blended with user reviews.
  year, genre, description, color1/color2 poster gradient, featured), `reviews` (1–5 rating + optional body,
  one per user per item). Ratings/averages are computed from `reviews`, never stored.
- `templates/`: `base.html`, `_nav.html` (shared header), `_macros.html` (`poster`, `card`), `index.html`, `browse.html`, `item.html`, `bookmarks.html`, `signup.html`, `login.html`. Jinja autoescapes all data.
- Passwords: Werkzeug `generate_password_hash` / `check_password_hash` in `app.py`; `db.py` only stores the hash.
- Auth: Flask signed-cookie session, `session["user"] = {id, name}` set by `log_in()` (clears session first).
  Signup logs you in. `POST /logout`. Header shows name + Log out when logged in.
  `SECRET_KEY` env var; without it a random key is used (everyone logged out on restart).
- Rating scale is 1–5 everywhere.

## Style (keep new pages consistent)
Plain editorial / print look. The user explicitly wants it to **not look AI-generated**: no gradients on backgrounds
or buttons, no glassmorphism/blur, no pill badges, no glowing shadows, no stat-number tiles, no gradient CTA banners,
no avatar circles, no coloured dot after the logo, no em-dash marketing copy.
- Colours are CSS variables in `:root`: paper `#f5f2eb`, ink `#1c1b19`, muted `#6b665c`, rule `#d8d2c4`, one accent purple `#5b3fa6` (dark: `#b39cf0`). Errors stay red.
- Dark mode follows the OS setting (`prefers-color-scheme`) by redefining the same variables. Never hard-code a colour:
  add a variable to both `:root` blocks. (Only exception: white poster titles.)
- Fonts: Source Serif 4 (`--serif`) for logo, headings, descriptions, review quotes; IBM Plex Sans for UI text.
- Structure via thin rules (1px `--rule`, 2px ink above section headings), square-ish corners (3–4px), no shadows.
- Buttons: solid ink, hover turns accent; `.ghost` = outline; `.small`, `.full` modifiers.
- Reusable classes: `.navbar`, `.logo`, `.button`, `.kicker` (small uppercase accent label), `.poster` (`--c1`/`--c2`,
  `.square` for albums), `.card` (auto-numbered via CSS counter), `.row` / `.row-head`, `.stars`, `.meta`, `.subtitle`,
  `.form-error`, `.sr-only`.
- Breakpoints: 900px (hide nav links + search, stack hero) and 480px (phones).

## Running and checking
- `python app.py` → http://localhost:5500 (preview config `critique` in `.claude/launch.json`).
- `python test_app.py` → prints `ok`.
- PostgreSQL 18 is installed on the user's machine (`C:\Program Files\PostgreSQL\18`, localhost:5432, password auth) but not used yet.

## Status / TODO
- [x] Item pages, review form + delete, bookmarks, like/dislike on reviews, browse pages. (Test suite extended but NOT yet run: no Python on the dev machine PATH.)
- [ ] Search, "See all" for latest reviews, recommendations of any kind.
- [ ] Recommendations: nothing implemented yet.
- [ ] Connect PostgreSQL: `psycopg`, run `schema.sql`, implement the `TODO(db)`s in `db.py`.
- [ ] Real cover images (posters are gradient + title for now).
