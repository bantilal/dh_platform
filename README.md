# 🌿 Digital Heroes — Full Stack Platform

> **Stack:** Django 6.x · PostgreSQL (Supabase) · JWT Auth · No DRF Serializers · Vanilla JS Frontend  
> **Theme:** Charity-emotion driven — Clean, Modern, Not a traditional golf website  
> **Live DB:** Supabase PostgreSQL  

---

## 📁 Project Structure

```
dh_platform/
├── manage.py
├── requirements.txt
├── seed_data.py              ← Dummy data script
├── .env                      ← Your local config (fill this)
├── .env.example              ← Template
│
├── dh_platform/              # Project config
│   ├── settings.py           # No decouple — uses os.environ
│   ├── urls.py               # / → frontend  |  /api/ → REST
│   └── wsgi.py
│
├── api/                      # API URL aggregator
│   └── urls.py               # All /api/ routes in one place
│
├── authentication/           # User auth + management
│   ├── models.py             # AbstractUser with email login
│   ├── views.py              # register, login, logout, CRUD
│   ├── utils.py              # @jwt_required, @admin_required
│   └── urls.py
│
├── subscriptions/            # Plans, payments, prize pool
├── scores/                   # Golf score management (rolling 5)
├── draws/                    # Monthly draw engine
├── charities/                # Charity directory + donations
├── winners/                  # Winner verification + payouts
├── dashboard/                # Aggregated dashboards + reports
├── frontend/                 # Django HTML page views
│
├── static/
│   ├── css/style.css         # Charity-emotion theme
│   └── js/app.js             # API helpers, auth, sidebar
│
└── templates/
    ├── base.html
    ├── index.html
    ├── auth/login.html
    ├── auth/register.html
    ├── user/dashboard.html
    ├── user/scores.html
    ├── user/draws.html
    ├── user/charity.html
    ├── user/subscription.html
    ├── user/winnings.html
    └── admin_panel/
        ├── dashboard.html
        ├── users.html
        ├── draws.html
        ├── charities.html
        └── winners.html
```

---

## 🚀 Setup Instructions (Windows)

### Step 1 — Extract & Open folder

```cmd
cd dh_platform
```

### Step 2 — Create virtual environment

```cmd
python -m venv venv
venv\Scripts\activate
```

> ✅ You will see `(venv)` in your terminal

### Step 3 — Install dependencies

```cmd
pip install -r requirements.txt
```

> ⚠️ Make sure venv is active before running this

### Step 4 — Configure `.env` file

Open `.env` file (already present) and update:

```env
SECRET_KEY=dh-secret-key-change-in-production-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase PostgreSQL
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=YOUR_SUPABASE_PASSWORD_HERE
DB_HOST=db.wybdwpnrsrimsklgiiny.supabase.co
DB_PORT=5432

STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

> 🔑 Replace `YOUR_SUPABASE_PASSWORD_HERE` with the password you set when creating the Supabase project

### Step 5 — Run migrations (creates tables in Supabase)

```cmd
python manage.py makemigrations
python manage.py migrate
```

Expected output:
```
Applying authentication.0001_initial... OK
Applying subscriptions.0001_initial... OK
Applying scores.0001_initial... OK
...
```

### Step 6 — Create admin superuser

```cmd
python manage.py createsuperuser
```

Fill in:
```
Email:    admin@digitalheroes.com
Username: admin@digitalheroes.com
Password: Admin@2026!
```

### Step 7 — Seed dummy data

```cmd
python seed_data.py
```

Expected output:
```
Seeding database...
[1/6] Creating charities... ✅ 8 charities
[2/6] Creating users...     ✅ 6 users
[3/6] Creating subscriptions... ✅ 6 subscriptions
[4/6] Creating golf scores... ✅ 30 scores
[5/6] Creating draws...     ✅ 2 draws
[6/6] Creating winners...   ✅ 3 winners
SEED COMPLETE!
```

### Step 8 — Collect static files

```cmd
python manage.py collectstatic --noinput
```

### Step 9 — Run server

```cmd
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 🌐 Page URLs

| Page | URL |
|------|-----|
| 🏠 Home (Public) | http://127.0.0.1:8000/ |
| 🔐 Login | http://127.0.0.1:8000/login/ |
| 📝 Register | http://127.0.0.1:8000/register/ |
| 📊 User Dashboard | http://127.0.0.1:8000/dashboard/ |
| ⛳ My Scores | http://127.0.0.1:8000/scores/ |
| 🎯 Draws | http://127.0.0.1:8000/draws/ |
| 💚 Charity | http://127.0.0.1:8000/charity/ |
| 💳 Subscription | http://127.0.0.1:8000/subscription/ |
| 🏆 Winnings | http://127.0.0.1:8000/winnings/ |
| 🛡 Admin Overview | http://127.0.0.1:8000/admin-panel/ |
| 👥 Admin Users | http://127.0.0.1:8000/admin-panel/users/ |
| 🎲 Admin Draw Engine | http://127.0.0.1:8000/admin-panel/draws/ |
| 💚 Admin Charities | http://127.0.0.1:8000/admin-panel/charities/ |
| ✅ Admin Winners | http://127.0.0.1:8000/admin-panel/winners/ |
| ⚙️ Django Admin | http://127.0.0.1:8000/admin/ |

---

## 🔑 Test Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@digitalheroes.com | Admin@2026! |
| Subscriber | john@example.com | Test@1234 |
| Subscriber | sarah@example.com | Test@1234 |
| Subscriber | mike@example.com | Test@1234 |
| Subscriber | priya@example.com | Test@1234 |
| Subscriber | emma@example.com | Test@1234 |
| Subscriber | tom@example.com | Test@1234 |

---

## 🔌 REST API Reference

Base URL: `http://127.0.0.1:8000/api/`

All requests: `Content-Type: application/json`  
Protected routes: `Authorization: Bearer <access_token>`

### Auth `/api/auth/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `register/` | Public | Register new user |
| POST | `login/` | Public | Login → returns JWT tokens |
| GET | `check-auth/` | JWT | Verify token |
| POST | `logout/` | JWT | Blacklist refresh token |
| POST | `add-user/` | Admin | Create user |
| POST | `view-user/` | Admin | View user by ID |
| POST | `user-list/` | Admin | Paginated user list |
| POST | `edit-user/` | JWT | Edit profile |
| POST | `user-status/` | Admin | Toggle active/inactive |

### Subscriptions `/api/subscriptions/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `create/` | JWT | Subscribe (monthly/yearly) |
| GET | `view/` | JWT | My subscription |
| POST | `list/` | Admin | All subscriptions |
| POST | `cancel/` | JWT | Cancel subscription |
| GET | `payment-history/` | JWT | Payment history |
| GET | `prize-pool/` | Admin | Prize pool breakdown |

### Scores `/api/scores/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `add-score/` | Subscriber | Add golf score (1–45) |
| POST | `edit-score/` | Subscriber | Edit existing score |
| POST | `delete-score/` | Subscriber | Delete score |
| GET | `score-list/` | JWT | Last 5 scores |
| POST | `admin-edit-score/` | Admin | Admin edits any score |

### Draws `/api/draws/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `create-draw/` | Admin | Configure monthly draw |
| POST | `simulate-draw/` | Admin | Pre-publish simulation |
| POST | `publish-draw/` | Admin | Run official draw |
| POST | `view-draw/` | JWT | View draw details |
| GET | `draw-list/` | JWT | List all draws |

### Charities `/api/charities/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `add-charity/` | Admin | Add charity |
| POST | `edit-charity/` | Admin | Edit charity |
| POST | `delete-charity/` | Admin | Delete charity |
| GET | `view-charity/` | Public | View charity + events |
| POST | `charity-list/` | Public | List/search charities |
| POST | `donate/` | JWT | Extra donation |

### Winners `/api/winners/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `submit-proof/` | JWT | Upload winner proof |
| GET | `view-verification/` | JWT | My verification status |
| POST | `verification-list/` | Admin | All verifications |
| POST | `approve-verification/` | Admin | Approve submission |
| POST | `reject-verification/` | Admin | Reject with reason |
| POST | `mark-payout-paid/` | Admin | Mark prize as paid |

### Dashboard `/api/dashboard/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `user-dashboard/` | JWT | Full user dashboard |
| GET | `admin-dashboard/` | Admin | Admin overview stats |
| POST | `admin-reports/` | Admin | Reports & analytics |

---

## ✅ PRD Requirements Checklist

| Requirement | Status |
|-------------|--------|
| Subscription Engine (Monthly + Yearly) | ✅ |
| Score Entry (1–45 Stableford) | ✅ |
| Rolling 5-score logic (oldest auto-removed) | ✅ |
| One score per date (duplicate check) | ✅ |
| Reverse chronological score display | ✅ |
| Random Draw algorithm | ✅ |
| Algorithmic Draw (frequency-weighted) | ✅ |
| Draw simulation before publish | ✅ |
| Jackpot rollover (5-match unclaimed) | ✅ |
| Prize pool: 40% / 35% / 25% split | ✅ |
| Multiple winners split equally | ✅ |
| Charity selection at signup | ✅ |
| Minimum 10% charity contribution | ✅ |
| Extra voluntary donations | ✅ |
| Charity directory with search/filter | ✅ |
| Winner proof upload | ✅ |
| Admin approve/reject verification | ✅ |
| Payment status tracking (pending → paid) | ✅ |
| User dashboard (all 5 modules) | ✅ |
| Admin dashboard (all controls) | ✅ |
| Reports & analytics | ✅ |
| Mobile-first responsive design | ✅ |
| JWT authentication | ✅ |
| Role-based access (public/subscriber/admin) | ✅ |
| No DRF serializers (manual JSON responses) | ✅ |
| Soft delete on all models | ✅ |
| Error handling & edge cases | ✅ |

---

## 🗄️ Supabase Database Setup

### Get connection details
1. Go to: https://supabase.com/dashboard/project/wybdwpnrsrimsklgiiny
2. Click **"Connect"** button
3. Select **"Direct"** tab
4. Copy the host: `db.wybdwpnrsrimsklgiiny.supabase.co`

### Update `.env`
```env
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_password
DB_HOST=db.wybdwpnrsrimsklgiiny.supabase.co
DB_PORT=5432
```

### SSL is required — already configured in settings.py
```python
'OPTIONS': {
    'sslmode': 'require',
}
```

---

## ⚠️ Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `No module named 'decouple'` | Already fixed — settings.py uses `os.environ` now |
| `No module named 'frontend'` | Run: `mkdir frontend` and create `__init__.py` inside |
| `Django version 6.x installed` | Run: `pip install Django==4.2.16` |
| `SSL connection required` | Already added `sslmode: require` in settings.py |
| `could not connect to server` | Use Session Pooler host from Supabase instead |
| `UserManager missing username` | Pass `username=email.split('@')[0]` in create_user |

---

## 🎨 Design Theme

Per PRD spec — **emotion-driven, not a traditional golf website:**

| Token | Value | Usage |
|-------|-------|-------|
| Primary | `#059669` Emerald | Charity / Nature |
| Accent | `#7c3aed` Violet | Premium / Draws |
| Gold | `#f59e0b` | Jackpot / Prizes |
| Background | `#07090f` Near-black | App background |
| Font | Outfit + DM Serif Display | Modern + Elegant |

**No golf clichés** — fairways, plaid, club imagery not used as primary design language.

---

## 🔑 Key Architecture Decisions

- **No serializers** — all responses are manually built Python dicts → `JsonResponse`
- **Function-based views** with `@csrf_exempt`, `@require_http_methods`
- **Custom JWT decorators** — `@jwt_required`, `@admin_required`, `@subscriber_required`
- **URL style** — `add-score/`, `score-list/`, `edit-score/` (matches team convention)
- **Model style** — `soft_delete`, `created_at`, `updated_at`, `meta JSONField`
- **Validation** — `errors = {}` → field checks → `if errors: return JsonResponse(...)`
- **`/api/` prefix** — all APIs, clean frontend routes at root `/`

---

*Built for Digital Heroes — digitalheroes.co.in*