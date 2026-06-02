# Django API Template

A minimal starting point for a Python JSON API built on **Django 6**, **Django REST Framework**, and Django's built-in **ORM + migrations**, with interactive **OpenAPI docs** (Swagger UI / ReDoc) generated from the DRF serializers via **[drf-spectacular](https://github.com/tfranzel/drf-spectacular)**. Ships with two interchangeable backends — **SQLite** (a single local file, zero setup, the default) and **MySQL** (networked) — selected by one env var. See [Choosing a database](#choosing-a-database). Swap the engine/URL for Postgres/etc. when a project outgrows them.

The endpoints in `catalog/` (`/items`, `/manufacturers`) are scaffolding — delete them and replace with real domain models. The plumbing (project settings, DRF wiring, env-driven config, the `DATABASE_URL` switch, the admin) is the part worth keeping.

> **Coming from the Flask template?** This is the same API, the same data model, and the same two-backend story — re-expressed in Django idioms. SQLAlchemy → the Django ORM, Alembic → Django migrations, Pydantic + Spectree → DRF serializers + drf-spectacular. Plus the Django admin for free.

## Where to go

Once the server is up (`python manage.py runserver`, default port `8000`):

| URL | What |
| --- | --- |
| [`/apidoc/swagger`](http://127.0.0.1:8000/apidoc/swagger) | **Swagger UI** — interactive docs, click-to-try requests. |
| [`/apidoc/redoc`](http://127.0.0.1:8000/apidoc/redoc) | **ReDoc** — clean, readable reference. |
| [`/apidoc/openapi.json`](http://127.0.0.1:8000/apidoc/openapi.json) | Raw **OpenAPI spec** (feed it to codegen, Postman, etc.). |
| [`/admin/`](http://127.0.0.1:8000/admin/) | **Django admin** — CRUD UI for the models (needs a superuser; see [Admin](#admin)). |
| [`/healthz`](http://127.0.0.1:8000/healthz) | Liveness check — `{"status": "ok"}`. |

Both doc UIs are generated from the same DRF serializers — pick whichever you like. See [Endpoints](#endpoints) for the API routes themselves.

## Layout

| Path | Purpose |
| --- | --- |
| `manage.py` | Django's CLI entrypoint (`migrate`, `runserver`, `createsuperuser`, …). |
| `config/settings.py` | Settings: env-driven config, installed apps, `DATABASE_URL` parsing, DRF + spectacular. |
| `config/urls.py` | Root URL routing: admin, the docs, and `include()` of the app's routes. |
| `config/wsgi.py` / `asgi.py` | Server entrypoints (`gunicorn config.wsgi`). |
| `config/__init__.py` | PyMySQL-as-MySQLdb shim (keeps the MySQL driver pure-Python). |
| `catalog/models.py` | Django ORM models. |
| `catalog/serializers.py` | DRF serializers (validation + serialization, drive the docs). |
| `catalog/views.py` | DRF viewsets + the health view. Thin; query logic lives on the queryset. |
| `catalog/urls.py` | App routes (a DRF router) + `/healthz`. |
| `catalog/admin.py` | Admin registrations for the models. |
| `catalog/migrations/` | Generated migrations (checked in). |
| `requirements.txt` | Pinned dependencies. |
| `.env.example` | Copy to `.env` and edit. |

## Choosing a database

The backend is selected entirely by `DATABASE_URL` in `.env` — there is **one** switch and nothing else changes. `config/settings.py` parses it with [django-environ](https://django-environ.readthedocs.io/), which picks the right `ENGINE` from the URL scheme.

| | SQLite (default) | MySQL |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./django_app.db` | `mysql://root:root@127.0.0.1:3306/django_app` |
| Driver | stdlib `sqlite3` (no install) | `PyMySQL` (in `requirements.txt`) |
| Setup | none — a file is created on first migration | install + run a MySQL server |
| Good for | quick local dev, tests, demos | shared/staging/prod-like environments |

**To switch backends, change that one line in `.env` and re-run `python manage.py migrate`.** The MySQL driver ships in `requirements.txt`, so no reinstall is needed. The two backends are separate stores — data does not carry over between them.

A few details the template already handles for you:

- **SQLite path:** three slashes (`sqlite:///./django_app.db`) is relative to the working directory; four slashes is an absolute path. `*.db` files are gitignored.
- **Pure-Python MySQL:** Django's MySQL backend normally wants `mysqlclient` (a C extension). `config/__init__.py` installs `PyMySQL` as a drop-in (`pymysql.install_as_MySQLdb()`), so MySQL works with no build toolchain — the same choice the SQLite-by-default story makes elsewhere.
- **Migrations are dialect-agnostic.** Django generates and runs the same migrations against either backend; you don't manage batch/ALTER quirks by hand.

## Setup

### 1. Python venv

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```shell
cp .env.example .env
```

`.env.example` ships with SQLite active and MySQL commented out. It also holds Django's `SECRET_KEY` and `DEBUG`. Generate a real secret key for anything that leaves your machine:

```shell
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

Pick a database:

**Option A — SQLite (default; no server to install).** Nothing to edit — the copied `.env` already points at `sqlite:///./django_app.db`, and the file is created when you migrate. Skip to step 3.

**Option B — MySQL.** In `.env`, comment out the SQLite line and uncomment the MySQL one. Then install and start a local MySQL server:

```shell
brew install mysql
brew services start mysql
```

Create the database (the defaults assume the root account with password `root` — fine for local dev, change for anything real):

```shell
mysql -uroot -e "CREATE DATABASE django_app;"
mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';"
```

Edit the MySQL `DATABASE_URL` in `.env` if your user/password/port differs. The format is:

```
mysql://<user>:<password>@<host>:<port>/<database>
```

### 3. Run migrations

```shell
python manage.py migrate
```

This applies Django's built-in tables (admin, auth, sessions) plus the `items` and `manufacturers` tables from `catalog/migrations/`.

After editing models, generate a new migration and apply it:

```shell
python manage.py makemigrations
python manage.py migrate
```

Migrations are checked in under `catalog/migrations/` — commit them alongside the model changes that produced them.

### 4. Run the API

```shell
python manage.py runserver          # dev server with auto-reload, on http://127.0.0.1:8000
```

For a production-style run, use the bundled WSGI server (gunicorn):

```shell
gunicorn config.wsgi                # serves the application from config/wsgi.py
```

- Swagger UI: <http://127.0.0.1:8000/apidoc/swagger>
- ReDoc: <http://127.0.0.1:8000/apidoc/redoc>
- Raw OpenAPI spec: <http://127.0.0.1:8000/apidoc/openapi.json>
- Admin: <http://127.0.0.1:8000/admin/>
- Health: <http://127.0.0.1:8000/healthz>

The docs are generated by drf-spectacular from the DRF serializers in `catalog/serializers.py` and the viewsets in `catalog/views.py`. Add a serializer + viewset and it shows up in Swagger automatically.

## Admin

Django's admin is wired up out of the box (`catalog/admin.py` registers both models). Create a login, then browse to `/admin/`:

```shell
python manage.py createsuperuser
```

It's a full CRUD UI over your data with search and filters — one of the main reasons to reach for Django over a micro-framework. Lock it down (or remove `django.contrib.admin`) before exposing anything publicly.

## Debugging in PyCharm

A ready-made run configuration ships in `.idea/runConfigurations/`, so you can debug with PyCharm's native debugger straight away:

1. Pick **`runserver (debug)`** in the Run/Debug dropdown (top-right). If it isn't there yet, **File → Reload All from Disk**.
2. Set a breakpoint (click the gutter beside a line in, say, `catalog/views.py`).
3. **Run → Debug** (the green bug icon, or `⌃D`).
4. Hit an endpoint (`curl http://127.0.0.1:8000/items` or a browser) — execution stops at the breakpoint with the full frames/variables/console.

Prefer to build it by hand? **Run → Edit Configurations → `+` → Python**, set *Script path* to `manage.py`, *Parameters* to `runserver --noreload`, working directory to the project root, and the interpreter to your `.venv`. That's the same config the shipped XML defines.

> **Why `--noreload`?** Django's dev server runs your code in a child process so it can auto-restart on file changes. PyCharm's debugger attaches to the *parent*, so without `--noreload` your breakpoints silently never hit. `--noreload` collapses it to one process — breakpoints always work. The trade-off is no auto-reload, so restart the debugger after editing code.

On **PyCharm Professional** you can instead enable Django support (**Settings → Languages & Frameworks → Django**: project root, `config/settings.py`, `manage.py`) and add a **Django Server** run configuration. It debugs correctly *and* keeps auto-reload, launched the same way via Run → Debug.

## Data model

Two tables with a foreign key, to illustrate a relationship:

- **`manufacturers`** — `id`, `name` (unique), `state` (2-letter code).
- **`items`** — `id`, `name` (unique), `description`, `price`, `created_at`, plus `manufacturer_id`, a non-null FK into `manufacturers`.

Every item belongs to one manufacturer. `GET /items` and `GET /items/{id}` return the item's columns **plus** the manufacturer nested in (`{..., "manufacturer": {"id", "name", "state"}}`), eager-loaded with `select_related` in `catalog/views.py` to avoid N+1 queries. `POST /items` requires a valid `manufacturer_id` (400 if it doesn't exist — DRF's `PrimaryKeyRelatedField` validates it); create manufacturers first via `POST /manufacturers`. Deleting a manufacturer that still has items is blocked (`on_delete=PROTECT`).

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/healthz` | Liveness check (`{"status": "ok"}`). |
| `GET` | `/items` | List items (optional `?search=`). |
| `GET` | `/items/<id>` | One item, or 404. |
| `POST` | `/items` | Create an item (validates body; 400 on unknown manufacturer). |
| `GET` | `/manufacturers` | List manufacturers (optional `?search=`). |
| `GET` | `/manufacturers/<id>` | One manufacturer, or 404. |
| `POST` | `/manufacturers` | Create a manufacturer (validates body). |

Routes are registered with a DRF router (`catalog/urls.py`) configured with `trailing_slash=False`, so paths read `/items` and `/items/1` (no trailing slash), matching the Flask template. Request validation is handled by the serializers: a bad body returns `400` with DRF's field-keyed error list (e.g. `{"price": ["Ensure this value is greater than or equal to 0."]}`), and a missing row returns `404` (`{"detail": "No Item matches the given query."}`).

## Try it

A manufacturer must exist before an item can reference it:

```shell
# 1. create a manufacturer, note its "id" in the response
curl -X POST http://127.0.0.1:8000/manufacturers \
  -H 'Content-Type: application/json' \
  -d '{"name": "Acme Corp", "state": "CA"}'

# 2. create an item pointing at that manufacturer
curl -X POST http://127.0.0.1:8000/items \
  -H 'Content-Type: application/json' \
  -d '{"name": "Widget", "description": "a thing", "price": 9.99, "manufacturer_id": 1}'

curl http://127.0.0.1:8000/items     # each item includes its nested manufacturer
curl http://127.0.0.1:8000/items/1
curl 'http://127.0.0.1:8000/items?search=wid'   # case-insensitive name filter
```

Both list endpoints (`GET /items`, `GET /manufacturers`) take an optional `?search=` query param that does a case-insensitive `LIKE` on `name`. Django's `__icontains` escapes `%` and `_` in the search term, so they match themselves rather than acting as wildcards. Omitting it (or passing blank) returns everything.

Or just run `./seed.sh` (below), which does all of this for you.

### Seed sample data

`seed.sh` POSTs a few manufacturers and then items that reference them (so the foreign keys line up) to the running API, giving you data to look at. The API must be running and migrated first.

```shell
./seed.sh                                  # seeds http://127.0.0.1:8000 (Django's default)
BASE_URL=http://127.0.0.1:8099 ./seed.sh   # different host/port
```

Because it goes through HTTP, it works identically against SQLite or MySQL. Edit the `items=(...)` array in the script to change what gets inserted.

## Using this as a starting point

1. Clone or copy this directory into a new repo.
2. **Rename the database** — see below. Don't leave it as `django_app`, or every project off this template ends up sharing one database in your local MySQL.
3. Rename the `Item`/`Manufacturer` models in `catalog/models.py` (and the matching serializers/views) to your domain — or rename the whole `catalog` app.
4. Delete `catalog/migrations/0001_initial.py` and run `python manage.py makemigrations` to regenerate against your new models.
5. Want Postgres instead? Replace `PyMySQL` with `psycopg[binary]` in `requirements.txt` and use `postgres://...` in `DATABASE_URL`. django-environ maps it to Django's Postgres backend; nothing else changes.

### Renaming the database

> On **SQLite** there's nothing to rename: just point `DATABASE_URL` at a different filename (`sqlite:///./widgets.db`) and run `python manage.py migrate`. The steps below are for **MySQL**.

The template ships with a database named `django_app`. For a real project, pick a name that matches the repo (e.g. `widgets`, `invoicing`) so your local MySQL doesn't turn into a junk drawer.

1. **Create the new database in MySQL:**

   ```shell
   mysql -uroot -proot -e "CREATE DATABASE widgets;"
   ```

2. **Update `.env`** — change the last path segment of `DATABASE_URL`:

   ```
   DATABASE_URL=mysql://root:root@127.0.0.1:3306/widgets
   ```

3. **Update `.env.example`** to match, so anyone else cloning the repo gets the right default.

4. **Run migrations against the new database:**

   ```shell
   python manage.py migrate
   ```

The `default=` fallback for `DATABASE_URL` in `config/settings.py` is SQLite, so the only places the MySQL name appears are `.env` and `.env.example`.

## Managing dependencies

`requirements.txt` is a curated list of the direct dependencies, pinned to exact versions. When you `pip install` something new during development, add it (with its version) so the next clone reproduces your environment:

```shell
pip install <package>
pip show <package> | grep -i version    # grab the version to pin
```

Add the `package==version` line to `requirements.txt`. (Or `pip freeze > requirements.txt` if you'd rather pin the full transitive tree — just activate the venv first so you capture the right packages.)

To upgrade a pinned package later:

```shell
pip install --upgrade <package>
```

…then bump its line in `requirements.txt`.

## Design notes

- **Env-driven settings, one switch.** `config/settings.py` is the single source for config; django-environ reads `.env` and parses typed values. `DATABASE_URL` is the only knob that selects MySQL vs SQLite — `env.db()` turns it into Django's `DATABASES` dict. Don't read `os.environ` elsewhere.
- **Pure-Python MySQL driver.** `config/__init__.py` installs PyMySQL as `MySQLdb` so the MySQL backend needs no C build toolchain. It's a no-op under SQLite, so it runs unconditionally and early (before Django opens a connection).
- **Thin views, query logic on the queryset.** The viewsets in `catalog/views.py` are `ListModelMixin + RetrieveModelMixin + CreateModelMixin` (list/retrieve/create only — no update/destroy, matching the Flask template). The `?search=` filter and `select_related` eager-loading live on `get_queryset`, keeping the views declarative.
- **Serializers do validation, serialization, and docs.** `catalog/serializers.py` mirrors the Flask Pydantic schemas: `ManufacturerSerializer` is reused both standalone and nested inside `ItemSerializer`. In `ItemSerializer`, `manufacturer` is the nested read-only object and `manufacturer_id` is the writable FK (both pointing at the same model field), so a write validates the id exists — unknown id → 400 — and a read echoes both back, matching the Flask payload shape exactly.
- **Eager-load relationships.** Item reads use `select_related("manufacturer")` so the related row comes back in the same query (a JOIN) rather than one query per item. The admin's `ItemAdmin` does the same with `list_select_related`.
- **drf-spectacular for OpenAPI.** The schema is generated from the serializers + viewsets. `python manage.py spectacular --validate` checks it produces a clean spec; the `?search=` param is documented via `@extend_schema_view` in `catalog/views.py`.
- **The admin is included on purpose.** `django.contrib.admin` and the `catalog/admin.py` registrations give a CRUD UI for free — the headline Django feature. Remove the app and the registration if you don't want it.
- **`description` is an empty string, not null.** Following Django's convention for text fields (`blank=True, default=""`), an omitted item description comes back as `""` rather than `null`. This is the one intentional payload difference from the Flask template (which used `None`).
