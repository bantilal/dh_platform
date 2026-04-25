import json
import datetime
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth import get_user_model

from authentication.utils import jwt_required, admin_required
from .models import Subscription, PaymentHistory

User = get_user_model()

PLAN_PRICES = {'monthly': Decimal('9.99'), 'yearly': Decimal('89.99')}


def _calc_amounts(plan, charity_pct):
    amount       = PLAN_PRICES.get(plan, Decimal('9.99'))
    prize_amount = (amount * Decimal('40') / Decimal('100')).quantize(Decimal('0.01'))
    charity_amt  = (amount * Decimal(str(charity_pct)) / Decimal('100')).quantize(Decimal('0.01'))
    return amount, prize_amount, charity_amt


def _sub_dict(s):
    return {
        'subscription_id':  s.id, 'user_id': s.user_id,
        'plan': s.plan, 'status': s.status,
        'amount': str(s.amount),
        'charity_percent': str(s.charity_percent),
        'prize_pool_amount': str(s.prize_pool_amount),
        'charity_amount': str(s.charity_amount),
        'start_date': str(s.start_date), 'end_date': str(s.end_date),
        'renewal_date': str(s.renewal_date), 'auto_renew': s.auto_renew,
        'created_at': str(s.created_at),
    }


# ── Create Subscription ───────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@jwt_required
def create_subscription(request):
    try:
        data        = json.loads(request.body)
        user        = request.auth_user
        plan        = data.get('plan', '').strip()
        charity_pct = float(data.get('charity_percent', user.charity_percent))

        errors = {}
        if plan not in ('monthly', 'yearly'):
            errors['plan'] = 'Plan must be monthly or yearly'
        if charity_pct < 10:
            errors['charity_percent'] = 'Minimum 10% charity contribution required'
        if errors:
            return JsonResponse({'status': False, 'errors': errors}, status=200)

        Subscription.objects.filter(user_id=user.id, status='active').update(
            status='cancelled', updated_at=timezone.now())

        amount, prize_amt, charity_amt = _calc_amounts(plan, charity_pct)
        start = timezone.now().date()
        end   = start + (datetime.timedelta(days=365) if plan == 'yearly'
                         else datetime.timedelta(days=30))

        sub = Subscription.objects.create(
            user_id=user.id, plan=plan, status='active', amount=amount,
            charity_percent=charity_pct, prize_pool_amount=prize_amt,
            charity_amount=charity_amt, start_date=start, end_date=end, renewal_date=end,
        )
        User.objects.filter(id=user.id).update(role='subscriber', charity_percent=charity_pct)
        PaymentHistory.objects.create(
            user_id=user.id, subscription_id=sub.id, amount=amount,
            status='success', description=f'{plan.capitalize()} subscription',
        )
        return JsonResponse({'status': True, 'message': 'Subscription created successfully',
                             'data': _sub_dict(sub)}, status=201)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── View Subscription ─────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['GET', 'POST'])
@jwt_required
def view_subscription(request):
    try:
        user = request.auth_user
        sub  = Subscription.objects.filter(user_id=user.id, soft_delete=False).order_by('-id').first()
        if not sub:
            return JsonResponse({'status': True, 'message': 'No subscription found', 'data': None})
        return JsonResponse({'status': True, 'data': _sub_dict(sub)})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── List Subscriptions (Admin) ────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def list_subscriptions(request):
    try:
        data   = json.loads(request.body)
        page   = int(data.get('page', 1))
        limit  = int(data.get('limit', 10))
        status = data.get('status', '')
        plan   = data.get('plan', '')

        qs = Subscription.objects.filter(soft_delete=False).order_by('-id')
        if status: qs = qs.filter(status=status)
        if plan:   qs = qs.filter(plan=plan)

        total = qs.count()
        subs  = qs[(page - 1) * limit: page * limit]
        return JsonResponse({'status': True, 'current_page': page,
                             'total_pages': (total + limit - 1) // limit, 'total': total,
                             'data': [_sub_dict(s) for s in subs]})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── Cancel Subscription ───────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@jwt_required
def cancel_subscription(request):
    try:
        user = request.auth_user
        sub  = Subscription.objects.filter(user_id=user.id, status='active').first()
        if not sub:
            return JsonResponse({'status': False, 'error': 'No active subscription'}, status=200)
        sub.status = 'cancelled'
        sub.updated_at = timezone.now()
        sub.save()
        return JsonResponse({'status': True, 'message': 'Subscription cancelled'})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── Payment History ───────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['GET', 'POST'])
@jwt_required
def payment_history(request):
    try:
        user = request.auth_user
        hist = PaymentHistory.objects.filter(user_id=user.id).order_by('-id')
        return JsonResponse({'status': True, 'data': [{
            'payment_id': h.id, 'amount': str(h.amount), 'currency': h.currency,
            'status': h.status, 'description': h.description, 'date': str(h.created_at),
        } for h in hist]})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── Prize Pool Summary ────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['GET', 'POST'])
@admin_required
def prize_pool_summary(request):
    try:
        qs = Subscription.objects.filter(status='active', end_date__gte=timezone.now().date())
        t  = qs.aggregate(p=Sum('prize_pool_amount'), c=Sum('charity_amount'), a=Sum('amount'))
        prize = t['p'] or Decimal('0')
        return JsonResponse({'status': True, 'data': {
            'active_subscribers':  qs.count(),
            'total_prize_pool':    str(prize),
            'total_charity_pool':  str(t['c'] or Decimal('0')),
            'prize_5_match':       str((prize * Decimal('0.40')).quantize(Decimal('0.01'))),
            'prize_4_match':       str((prize * Decimal('0.35')).quantize(Decimal('0.01'))),
            'prize_3_match':       str((prize * Decimal('0.25')).quantize(Decimal('0.01'))),
        }})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)
