import os
import django
import sys
import datetime
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dh_platform.settings')
django.setup()

from django.utils import timezone
from django.db.models import Sum

from authentication.models import User
from charities.models import Charity
from subscriptions.models import Subscription, PaymentHistory
from scores.models import GolfScore
from draws.models import Draw, DrawParticipant, DrawWinner
from winners.models import WinnerVerification

print("Seeding database...")

# 1. Charities
print("\n[1/6] Creating charities...")
charities_data = [
    {"name": "GreenWorld Foundation", "category": "Environment",  "bio": "Fighting climate change", "featured": True},
    {"name": "Children First UK",     "category": "Children",     "bio": "Every child a fair start", "featured": True},
    {"name": "Shelter and Hope",      "category": "Homelessness", "bio": "Ending homelessness UK",   "featured": False},
    {"name": "Mind Matters",          "category": "Mental Health","bio": "Supporting mental wellbeing","featured": False},
    {"name": "Ocean Rescue",          "category": "Environment",  "bio": "Cleaning our oceans",      "featured": False},
    {"name": "Foodbank Alliance",     "category": "Food Poverty", "bio": "No one should go hungry",  "featured": True},
    {"name": "Age Well UK",           "category": "Elderly",      "bio": "Supporting the elderly",   "featured": False},
    {"name": "Animal Rescue UK",      "category": "Animals",      "bio": "Rescuing animals UK",      "featured": False},
]
created_charities = []
for c in charities_data:
    obj, created = Charity.objects.get_or_create(
        name=c["name"],
        defaults={
            "description":    c["bio"] + ". We work hard to make a real difference.",
            "short_bio":      c["bio"],
            "category":       c["category"],
            "is_featured":    c["featured"],
            "total_received": Decimal("5000.00"),
        }
    )
    created_charities.append(obj)
    print(f"  {'Created' if created else 'Exists'}: {obj.name}")

# 2. Users
print("\n[2/6] Creating users...")
users_data = [
    {"first": "John",  "last": "Smith",  "email": "john@example.com"},
    {"first": "Sarah", "last": "Chen",   "email": "sarah@example.com"},
    {"first": "Mike",  "last": "OBrien", "email": "mike@example.com"},
    {"first": "Priya", "last": "Patel",  "email": "priya@example.com"},
    {"first": "Emma",  "last": "Davies", "email": "emma@example.com"},
    {"first": "Tom",   "last": "Walsh",  "email": "tom@example.com"},
]
created_users = []
for i, u in enumerate(users_data):
    if not User.objects.filter(email=u["email"]).exists():

        # Auto username email se banao
        username = u["email"].split("@")[0] + str(i)

        user = User.objects.create_user(
            username        = username,       # 👈 yeh add kiya
            email           = u["email"],
            password        = "Test@1234",
            first_name      = u["first"],
            last_name       = u["last"],
            role            = "subscriber",
            charity_id      = created_charities[i % len(created_charities)].id,
            charity_percent = Decimal("10.00"),
            contact_no      = f"077009000{i}",
            country_code    = "+44",
        )
        created_users.append(user)
        print(f"  Created: {user.email}")
    else:
        user = User.objects.get(email=u["email"])
        created_users.append(user)
        print(f"  Exists:  {user.email}")

# 3. Subscriptions
print("\n[3/6] Creating subscriptions...")
plans = ["monthly", "monthly", "yearly", "monthly", "yearly", "monthly"]
amounts = {"monthly": Decimal("9.99"), "yearly": Decimal("89.99")}

for i, user in enumerate(created_users):
    if not Subscription.objects.filter(user_id=user.id).exists():
        plan        = plans[i]
        amount      = amounts[plan]
        prize       = (amount * Decimal("40") / Decimal("100")).quantize(Decimal("0.01"))
        charity_amt = (amount * Decimal("10") / Decimal("100")).quantize(Decimal("0.01"))
        start = timezone.now().date() - datetime.timedelta(days=15)
        end   = start + (datetime.timedelta(days=365) if plan == "yearly" else datetime.timedelta(days=30))
        sub = Subscription.objects.create(
            user_id=user.id, plan=plan, status="active",
            amount=amount, charity_percent=Decimal("10.00"),
            prize_pool_amount=prize, charity_amount=charity_amt,
            start_date=start, end_date=end, renewal_date=end,
        )
        PaymentHistory.objects.create(
            user_id=user.id, subscription_id=sub.id,
            amount=amount, status="success",
            description=f"{plan.capitalize()} subscription",
        )
        User.objects.filter(id=user.id).update(role="subscriber")
        print(f"  Created: {user.email} -> {plan} (£{amount})")

# 4. Golf Scores
print("\n[4/6] Creating golf scores...")
scores_list = [
    [32, 28, 35, 30, 27],
    [25, 31, 29, 33, 22],
    [38, 35, 40, 37, 34],
    [20, 24, 22, 26, 18],
    [30, 28, 33, 31, 29],
    [42, 38, 40, 35, 44],
]
for i, user in enumerate(created_users):
    scores = scores_list[i % len(scores_list)]
    for j, score_val in enumerate(scores):
        score_date = timezone.now().date() - datetime.timedelta(days=j * 4)
        if not GolfScore.objects.filter(user_id=user.id, score_date=score_date).exists():
            GolfScore.objects.create(user_id=user.id, score=score_val, score_date=score_date)
    print(f"  Scores for {user.email}: {scores}")

# 5. Draws
print("\n[5/6] Creating draws...")
pool = Subscription.objects.filter(status="active").aggregate(t=Sum("prize_pool_amount"))["t"] or Decimal("0")

draw, created = Draw.objects.get_or_create(
    draw_month=4, draw_year=2026,
    defaults={
        "title": "April 2026 Draw", "draw_type": "random",
        "status": "published", "winning_numbers": [7, 14, 22, 31, 38],
        "prize_pool_total": pool, "jackpot_rollover": Decimal("0"),
        "jackpot_claimed": False, "published_at": timezone.now(),
    }
)
print(f"  {'Created' if created else 'Exists'}: April 2026 Draw -> [7, 14, 22, 31, 38]")

for user in created_users:
    scores_qs = list(GolfScore.objects.filter(user_id=user.id).order_by("-score_date").values_list("score", flat=True)[:5])
    if scores_qs:
        DrawParticipant.objects.get_or_create(
            draw_id=draw.id, user_id=user.id,
            defaults={"submitted_scores": scores_qs}
        )

Draw.objects.get_or_create(
    draw_month=5, draw_year=2026,
    defaults={
        "title": "May 2026 Draw", "draw_type": "random",
        "status": "draft", "prize_pool_total": pool,
        "jackpot_rollover": Decimal("280.00"),
    }
)
print("  Created: May 2026 Draw (upcoming)")

# 6. Winners
print("\n[6/6] Creating winners...")
winner_configs = [
    (created_users[0], "4_match", Decimal("245.00"), "pending"),
    (created_users[1], "3_match", Decimal("87.50"),  "approved"),
    (created_users[2], "3_match", Decimal("87.50"),  "approved"),
]
for user, match_type, prize, status in winner_configs:
    w, _ = DrawWinner.objects.get_or_create(
        draw_id=draw.id, user_id=user.id,
        defaults={"match_type": match_type, "prize_amount": prize}
    )
    if not WinnerVerification.objects.filter(user_id=user.id, draw_id=draw.id).exists():
        WinnerVerification.objects.create(
            user_id=user.id, draw_id=draw.id, draw_winner_id=w.id,
            match_type=match_type, prize_amount=prize,
            status=status, payment_status="pending",
        )
    print(f"  Winner: {user.email} -> {match_type} -> £{prize}")

# Done
print("\n" + "="*50)
print("SEED COMPLETE!")
print("="*50)
print(f"  Charities:     {Charity.objects.count()}")
print(f"  Users:         {User.objects.count()}")
print(f"  Subscriptions: {Subscription.objects.count()}")
print(f"  Scores:        {GolfScore.objects.count()}")
print(f"  Draws:         {Draw.objects.count()}")
print(f"  Winners:       {DrawWinner.objects.count()}")
print("\nLogin Credentials:")
print("  Admin: admin@digitalheroes.com / Admin@2026!")
print("  User:  john@example.com / Test@1234")
print("  User:  sarah@example.com / Test@1234")
print("="*50)