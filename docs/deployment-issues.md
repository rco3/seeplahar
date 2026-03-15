# Deployment Issues Log — RRP1 (2026-03-15)

Captured from initial deployment of Seeplahar to RedRocketPi1 (Debian 13 trixie, aarch64).

---

## 1. django-tailwind not installed by first pip install

**Symptom:** `ModuleNotFoundError: No module named 'tailwind'` on first `manage.py migrate`.

**Cause:** `pip install -q -r requirements.txt` silently failed to install `django-tailwind[reload]`
(and several other packages) in the first pass, likely a network/timeout issue against piwheels.

**Fix:** Ran `pip install django-tailwind[reload]` explicitly; then re-ran the full
`pip install -r requirements.txt` until all packages were present. Added `libcairo2-dev`
system package first, as `reportlab` depends on `pycairo` which needs the Cairo dev headers
on aarch64 Debian.

---

## 2. django-htmx-autocomplete version conflict with Django 5.0

**Symptom:** pip auto-upgraded Django to 6.0.3 when installing `django-htmx-autocomplete`.

**Cause:** `django-htmx-autocomplete==1.0.17` requires `Django>=5.1`. The local dev environment
had version 0.8.3 which is compatible with Django 5.0.x.

**Fix:** Pinned `django-htmx-autocomplete==0.8.3` on RRP1 to match the dev environment.
Worth watching if Django is ever upgraded to 5.1+.

---

## 3. Divergent users.0001_initial between master and feature branch

**Symptom:** After first `migrate` (against master), `users_customer` table did not exist
despite `django_migrations` recording `users.0001_initial` as applied. Feature branch push
then failed with `ProgrammingError: relation "users_customer" does not exist` on `media.0002`.

**Cause:** The `users.0001_initial` migration in master was a different, older file (only
creating `CustomUser`) than the one in the feature branch (which also creates `Customer`,
`Partner`, `ContactInfo`, etc.). Django saw the migration as already applied and skipped it.

**Fix:** Dropped and recreated the database, then ran `migrate` fresh against the feature
branch code. All migrations applied cleanly in one pass.

**Lesson:** When migration files are rewritten/replaced rather than added (squash or history
rewrite), always deploy to a fresh database or fake/migrate manually.

---

## 4. loaddata failed on stale taxon.Synonym permissions

**Symptom:** `loaddata` failed with `ContentType matching query does not exist` for
`('taxon', 'synonym')`. The `taxon.Synonym` model was deleted in migration `taxon.0003`.

**Cause:** The local dev database still had `auth.Permission` records (and user M2M entries)
for the deleted Synonym model. The dump used `--natural-foreign`, which resolves permissions
by content type natural key — but that content type no longer exists in production.

**Fix:** On the local dev machine, deleted the stale content type and its permissions, then
removed them from all users' `user_permissions` M2M. Re-dumped with
`--natural-foreign --exclude contenttypes --exclude auth.permission`.

---

## 5. loaddata conflicted with existing content types

**Symptom (intermediate attempt):** Tried dumping *with* contenttypes to avoid issue #4.
`loaddata` then failed with `duplicate key value violates unique constraint` on
`django_content_type`.

**Cause:** `migrate` had already auto-created content types in the fresh DB. Loading a dump
that also contained them caused PK/uniqueness conflicts.

**Fix:** Reverted to the correct approach: exclude contenttypes from dump, fix the stale
permissions at source (issue #4 above), and use natural foreign keys.

---

## 6. staticfiles/css modified by collectstatic blocked subsequent pushes

**Symptom:** `git push rrp1 master` rejected with
`Working directory has unstaged changes` after every deploy that ran `collectstatic`.

**Cause:** `staticfiles/css/dist/styles.css` is a tracked git file, but `collectstatic`
regenerates it. The `receive.denyCurrentBranch updateInstead` setting refuses to overwrite
a dirty working tree.

**Fix:**
- Added a `pre-receive` hook on RRP1 that runs `git checkout -- .` before each push.
- Added `staticfiles/`, `debug.log`, `gunicorn.ctl`, and `__pycache__/` to
  `/home/goddard/seeplahar/.git/info/exclude` (local-only gitignore, doesn't affect the repo).

**Long-term:** `staticfiles/` should be added to `.gitignore` and removed from tracking.

---

## 7. nginx default site intercepted all requests

**Symptom:** `/api/auth/token/` and `/labels/diagnose/` returned nginx 404, not Django.
Home page returned 200 (nginx default page, not Django).

**Cause:** Debian's nginx ships with a `default` site enabled. Our seeplahar site uses
`server_name RedRocketPi1.local`, so requests from `curl http://localhost/` hit the default
site instead.

**Fix:** `sudo rm /etc/nginx/sites-enabled/default`. Added `default_server` to the seeplahar
nginx config so it handles all port-80 traffic.

---

## 8. /accounts/login/ 500 error

**Symptom:** Any page requiring login caused a 500 instead of redirecting to the login page.
`GenericListView` was parsing `/accounts/login/` as `app_name=accounts, model_name=login`.

**Cause:** Django's default `LOGIN_URL` is `/accounts/login/`, but the app's login view is
at `/login/`. `LOGIN_URL` was not set in settings, so Django's default was used.

**Fix:** Added `LOGIN_URL = '/login/'` to `seeplahar/settings/base.py`.

---

## 9. Static files returning 403 Forbidden

**Symptom:** All `/static/` requests returned 403. CSS, JS, and images all missing.

**Cause:** nginx runs as `www-data`. The home directory `/home/goddard` had default `700`
permissions, blocking `www-data` from traversing into it to reach `staticfiles/`.

**Fix:** `chmod o+x /home/goddard` — adds the execute (traverse) bit for others without
exposing home directory contents.

---

## 10. htmx.min.js missing from repo

**Symptom:** `ValueError: Missing staticfiles manifest entry for 'js/htmx.min.js'` — 500
on every page. WhiteNoise's `CompressedManifestStaticFilesStorage` raises on any referenced
static file not in the manifest.

**Cause:** `htmx.min.js` was referenced in `base.html` via `{% static %}` but was never
committed to git (not in `static/js/`).

**Fix:** Downloaded htmx 1.9.12 from unpkg and committed it to `static/js/htmx.min.js`.

---

## 11. lpr not installed (cups-bsd missing)

**Symptom:** Print jobs sent from the UI silently failed. Shell test gave
`PrintingError: lpr not found. CUPS does not appear to be installed.`

**Cause:** `cups-client` was installed but does not include `lpr` on Debian 13.
`lpr` is in the separate `cups-bsd` package.

**Fix:** `sudo apt-get install -y cups-bsd`.

---

## 12. Madeleine's CUPS only listening on localhost

**Symptom:** RRP1 could not reach Madeleine's CUPS at port 631.
`curl http://192.168.1.175:631/...` returned connection refused.

**Cause:** `/etc/cups/cupsd.conf` had `Listen localhost:631` — standard default on
Debian, only accepts local connections.

**Fix:** Changed to `Port 631` and added `Allow from @LOCAL` to the root `<Location />`
block. Restarted CUPS.

---

## System packages required beyond base Debian 13

```
postgresql postgresql-contrib
nginx
cups-bsd          # provides lpr
librsvg2-bin      # provides rsvg-convert
libpq-dev         # psycopg2 build dep (binary wheel also works)
libcairo2-dev     # reportlab/pycairo build dep on aarch64
python3-venv python3-pip
git
avahi-utils       # optional, useful for LAN printer discovery
```
