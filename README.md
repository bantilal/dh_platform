# 🌿 Digital Heroes — Full Stack Platform

> **Stack:** Django 4.2 · PostgreSQL · JWT Auth · No DRF Serializers · Vanilla JS Frontend
> **Theme:** Charity-emotion driven — Clean, Modern, Not a traditional golf website

---

## 📁 Project Structure

```
dh_platform/
├── manage.py
├── requirements.txt
├── .env.example
│
├── dh_platform/              # Project config
│   ├── settings.py
│   ├── urls.py               # Routes: / → frontend, /api/ → REST
│   └── wsgi.py
│
├── api/                      # API URL aggregator
│   └── urls.py               # All /api/ routes in one place
│
├── authentication/           # User auth + management
│   ├── models.py             # Custom AbstractBaseUser
│   ├── views.py              # register, login, logout, CRUD (no serializers)
│   ├── utils.py              # @jwt_required, @admin_required, @subscriber_required
│   └── urls.py
│
├── subscriptions/            # Plans, payments, prize pool
│   ├── models.py             # Subscription, PaymentHistory
│   ├── views.py
│   └── urls.py
│
├── scores/                   # Golf score management
│   ├── models.py             # GolfScore (unique_together: user+date)
│   ├── views.py              # Rolling 5-score logic, duplicate date check
│   └── urls.py
│
├── draws/                    # Monthly draw engine
│   ├── models.py             # Draw, DrawParticipant, DrawWinner
│   ├── views.py              # Random + Algorithmic engine, simulate, publish
│   └── urls.py
│
├── charities/                # Charity directory + donations
│   ├── models.py             # Charity, CharityEvent, CharityDonation
│   ├── views.py
│   └── urls.py
│
├── winners/                  # Winner verification + payouts
│   ├── models.py             # WinnerVerification
│   ├── views.py
│   └── urls.py
│
├── dashboard/                # Aggregated dashboards + reports
│   ├── views.py
│   └── urls.py
│
├── frontend/                 # Django HTML page views
│   ├── views.py              # All page renders
│   └── urls.py               # All page routes
│
├── static/
│   ├── css/style.css         # Complete charity-emotion theme
│   └── js/app.js             # API helpers, auth, toast, sidebar
│
└── templates/
    ├── base.html             # Shared sidebar layout
    ├── index.html            # Public home page
    ├── auth/
    │   ├── login.html
    │   └── register.html
    ├── user/
    │   ├── dashboard.html
    │   ├── scores.html
    │   ├── draws.html
    │   ├── charity.html
    │   ├── subscription.html
    │   └── winnings.html
    └── admin_panel/
        ├── dashboard.html
        ├── users.html
        ├── draws.html
        ├── charities.html
        └── winners.html
```

---

## 🚀 Setup Instructions

### 1. Create Virtual Environment
```bash
cd dh_platform
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your database credentials and secret key
```

### 4. Create PostgreSQL Database
```sql
CREATE DATABASE dh_platform_db;
```

### 5. Run Migrations
```bash
python manage.py makemigrations authentication
python manage.py makemigrations subscriptions
python manage.py makemigrations scores
python manage.py makemigrations draws
python manage.py makemigrations charities
python manage.py makemigrations winners
python manage.py makemigrations dashboard
python manage.py makemigrations frontend
python manage.py migrate
```

### 6. Create Admin Superuser
```bash
python manage.py createsuperuser
```

### 7. Collect Static Files
```bash
python manage.py collectstatic
```

### 8. Run Development Server
```bash
python manage.py runserver
```

---

## 🌐 URL Structure

### Frontend Pages (HTML)
| URL | Page |
|-----|------|
| `/` | Public home page |
| `/login/` | Login |
| `/register/` | Register + plan selection |
| `/dashboard/` | User dashboard |
| `/scores/` | Golf score management |
| `/draws/` | Monthly draws |
| `/charity/` | Charity selection |
| `/subscription/` | Subscription management |
| `/winnings/` | Winnings + proof submission |
| `/admin-panel/` | Admin overview |
| `/admin-panel/users/` | User management |
| `/admin-panel/draws/` | Draw engine |
| `/admin-panel/charities/` | Charity management |
| `/admin-panel/winners/` | Winner verification |

### REST API (JSON) — all under `/api/`
| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/auth/register/` | Public |
| POST | `/api/auth/login/` | Public |
| GET  | `/api/auth/check-auth/` | JWT |
| POST | `/api/auth/logout/` | JWT |
| POST | `/api/auth/add-user/` | Admin |
| POST | `/api/auth/view-user/` | Admin |
| POST | `/api/auth/user-list/` | Admin |
| POST | `/api/auth/edit-user/` | JWT |
| POST | `/api/auth/user-status/` | Admin |
| POST | `/api/subscriptions/create/` | JWT |
| GET  | `/api/subscriptions/view/` | JWT |
| POST | `/api/subscriptions/list/` | Admin |
| POST | `/api/subscriptions/cancel/` | JWT |
| GET  | `/api/subscriptions/payment-history/` | JWT |
| GET  | `/api/subscriptions/prize-pool/` | Admin |
| POST | `/api/scores/add-score/` | Subscriber |
| POST | `/api/scores/edit-score/` | Subscriber |
| POST | `/api/scores/delete-score/` | Subscriber |
| GET  | `/api/scores/score-list/` | JWT |
| POST | `/api/scores/admin-edit-score/` | Admin |
| POST | `/api/draws/create-draw/` | Admin |
| POST | `/api/draws/simulate-draw/` | Admin |
| POST | `/api/draws/publish-draw/` | Admin |
| POST | `/api/draws/view-draw/` | JWT |
| GET  | `/api/draws/draw-list/` | JWT |
| POST | `/api/charities/add-charity/` | Admin |
| POST | `/api/charities/edit-charity/` | Admin |
| POST | `/api/charities/delete-charity/` | Admin |
| GET  | `/api/charities/view-charity/` | Public |
| POST | `/api/charities/charity-list/` | Public |
| POST | `/api/charities/donate/` | JWT |
| POST | `/api/winners/submit-proof/` | JWT |
| GET  | `/api/winners/view-verification/` | JWT |
| POST | `/api/winners/verification-list/` | Admin |
| POST | `/api/winners/approve-verification/` | Admin |
| POST | `/api/winners/reject-verification/` | Admin |
| POST | `/api/winners/mark-payout-paid/` | Admin |
| GET  | `/api/dashboard/user-dashboard/` | JWT |
| GET  | `/api/dashboard/admin-dashboard/` | Admin |
| POST | `/api/dashboard/admin-reports/` | Admin |

---

## ✅ PRD Requirements Checklist

| Requirement | Status |
|-------------|--------|
| Subscription Engine (Monthly + Yearly) | ✅ |
| Stripe-ready payment structure | ✅ |
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
| Payment status tracking (pending→paid) | ✅ |
| User dashboard (all 5 modules) | ✅ |
| Admin dashboard (all controls) | ✅ |
| Reports & analytics | ✅ |
| Mobile-first responsive design | ✅ |
| JWT authentication | ✅ |
| Role-based access (public/subscriber/admin) | ✅ |
| No DRF serializers (manual JSON) | ✅ |
| Soft delete on all models | ✅ |
| Error handling & edge cases | ✅ |

---

## 🎨 Design Theme

Per PDF spec — **emotion-driven, not a traditional golf website**:
- **Primary colour:** Emerald green `#059669` (charity/nature)
- **Accent:** Violet `#7c3aed` (premium/draws)
- **Gold:** `#f59e0b` (jackpot/prizes)
- **Font:** Outfit (modern) + DM Serif Display (elegant headlines)
- **Background:** Near-black `#07090f` with subtle grid texture
- **No golf clichés** — fairways, plaid, club imagery NOT used as primary design language

---

## 🔑 Key Architecture

- **No serializers anywhere** — all API responses manually constructed as Python dicts → `JsonResponse`
- **Function-based views** with `@csrf_exempt`, `@require_http_methods`, custom JWT decorators
- **URL pattern style** matches your examples: `add-score/`, `score-list/`, `edit-score/`
- **Model style** matches your examples: `soft_delete`, `created_at/updated_at`, `meta JSONField`, `BigIntegerField` for FK references
- **Validation pattern**: `errors = {}` dict → check each field → `if errors: return JsonResponse(...)`
- **`/api/` prefix** for all API endpoints, clean frontend routes at root level
