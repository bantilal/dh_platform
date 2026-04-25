import json
import random
from decimal import Decimal
from collections import Counter
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum

from authentication.utils import jwt_required, admin_required
from .models import Draw, DrawParticipant, DrawWinner
from scores.models import GolfScore
from subscriptions.models import Subscription


# ── Draw Engine ───────────────────────────────────────────────────────────────
def _random_draw():
    pool = list(range(1, 46))
    return sorted(random.sample(pool, 5))


def _algorithmic_draw():
    active_ids = Subscription.objects.filter(
        status='active', end_date__gte=timezone.now().date()
    ).values_list('user_id', flat=True)
    all_scores = list(GolfScore.objects.filter(
        user_id__in=active_ids, soft_delete=False
    ).values_list('score', flat=True))
    if not all_scores:
        return _random_draw()
    freq    = Counter(all_scores)
    scores  = list(freq.keys())
    weights = [freq[s] for s in scores]
    selected = []
    attempts = 0
    while len(selected) < 5 and attempts < 1000:
        pick = random.choices(scores, weights=weights, k=1)[0]
        if pick not in selected:
            selected.append(pick)
        attempts += 1
    while len(selected) < 5:
        r = random.randint(1, 45)
        if r not in selected:
            selected.append(r)
    return sorted(selected)


def _distribute_prizes(draw_id, winning_numbers, prize_pool, rollover=Decimal('0')):
    participants = DrawParticipant.objects.filter(draw_id=draw_id)
    buckets = {'5_match': [], '4_match': [], '3_match': []}

    for p in participants:
        matched = len(set(p.submitted_scores) & set(winning_numbers))
        p.matched_count = matched
        if   matched >= 5: buckets['5_match'].append(p.user_id); p.is_winner = True
        elif matched == 4: buckets['4_match'].append(p.user_id); p.is_winner = True
        elif matched == 3: buckets['3_match'].append(p.user_id); p.is_winner = True
        p.save(update_fields=['matched_count', 'is_winner'])

    pool_5 = (prize_pool * Decimal('0.40')) + rollover
    pool_4 =  prize_pool * Decimal('0.35')
    pool_3 =  prize_pool * Decimal('0.25')

    created = []
    jackpot_claimed = False

    def _payout(match_type, user_ids, pool):
        if not user_ids: return
        per = (pool / Decimal(len(user_ids))).quantize(Decimal('0.01'))
        for uid in user_ids:
            DrawWinner.objects.create(draw_id=draw_id, user_id=uid,
                                      match_type=match_type, prize_amount=per)
            created.append({'user_id': uid, 'match_type': match_type, 'prize': str(per)})

    _payout('4_match', buckets['4_match'], pool_4)
    _payout('3_match', buckets['3_match'], pool_3)

    if buckets['5_match']:
        jackpot_claimed = True
        _payout('5_match', buckets['5_match'], pool_5)
        new_rollover = Decimal('0')
    else:
        new_rollover = pool_5

    return created, new_rollover, jackpot_claimed


# ── Create Draw ───────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def create_draw(request):
    try:
        data       = json.loads(request.body)
        title      = data.get('title', '').strip()
        draw_type  = data.get('draw_type', 'random')
        draw_month = int(data.get('draw_month', timezone.now().month))
        draw_year  = int(data.get('draw_year',  timezone.now().year))

        errors = {}
        if not title: errors['title'] = 'Title is required'
        if draw_type not in ('random', 'algorithmic'):
            errors['draw_type'] = 'Must be random or algorithmic'
        if Draw.objects.filter(draw_month=draw_month, draw_year=draw_year, soft_delete=False).exists():
            errors['draw'] = f'Draw for {draw_month}/{draw_year} already exists'
        if errors:
            return JsonResponse({'status': False, 'errors': errors}, status=200)

        pool_total = Subscription.objects.filter(
            status='active', end_date__gte=timezone.now().date()
        ).aggregate(t=Sum('prize_pool_amount'))['t'] or Decimal('0')

        prev_month = draw_month - 1 if draw_month > 1 else 12
        prev_year  = draw_year  if draw_month > 1 else draw_year - 1
        prev = Draw.objects.filter(draw_month=prev_month, draw_year=prev_year,
                                    jackpot_claimed=False, status='published').first()
        rollover = prev.jackpot_rollover if prev else Decimal('0')

        draw = Draw.objects.create(
            title=title, draw_type=draw_type, draw_month=draw_month,
            draw_year=draw_year, prize_pool_total=pool_total, jackpot_rollover=rollover,
        )
        return JsonResponse({'status': True, 'message': 'Draw configured successfully',
                             'data': {'draw_id': draw.id, 'title': draw.title,
                                      'draw_type': draw.draw_type, 'status': draw.status,
                                      'prize_pool_total': str(draw.prize_pool_total),
                                      'jackpot_rollover': str(draw.jackpot_rollover)}}, status=201)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── Simulate Draw ─────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def simulate_draw(request):
    try:
        data    = json.loads(request.body)
        draw_id = data.get('draw_id')
        if not draw_id:
            return JsonResponse({'status': False, 'error': 'draw_id required'}, status=200)
        draw = Draw.objects.get(id=draw_id, soft_delete=False)
        if draw.status == 'published':
            return JsonResponse({'status': False, 'error': 'Draw already published'}, status=200)

        numbers = _algorithmic_draw() if draw.draw_type == 'algorithmic' else _random_draw()
        draw.simulation_data = {'simulated_numbers': numbers, 'at': str(timezone.now())}
        draw.status = 'simulated'
        draw.save(update_fields=['simulation_data', 'status'])

        return JsonResponse({'status': True, 'message': 'Simulation complete',
                             'data': {'draw_id': draw.id, 'simulated_numbers': numbers,
                                      'prize_pool': str(draw.prize_pool_total),
                                      'jackpot_rollover': str(draw.jackpot_rollover)}})
    except Draw.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Draw not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── Publish Draw ──────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def publish_draw(request):
    try:
        data    = json.loads(request.body)
        draw_id = data.get('draw_id')
        admin   = request.auth_user
        draw    = Draw.objects.get(id=draw_id, soft_delete=False)
        if draw.status == 'published':
            return JsonResponse({'status': False, 'error': 'Already published'}, status=200)

        with transaction.atomic():
            numbers = _algorithmic_draw() if draw.draw_type == 'algorithmic' else _random_draw()
            draw.winning_numbers = numbers
            draw.status          = 'published'
            draw.published_by    = admin.id
            draw.published_at    = timezone.now()
            draw.save()

            active_users = Subscription.objects.filter(
                status='active', end_date__gte=timezone.now().date()
            ).values_list('user_id', flat=True)

            for uid in active_users:
                scores = list(GolfScore.objects.filter(user_id=uid, soft_delete=False)
                              .order_by('-score_date').values_list('score', flat=True)[:5])
                if scores:
                    DrawParticipant.objects.get_or_create(
                        draw_id=draw.id, user_id=uid,
                        defaults={'submitted_scores': scores},
                    )

            winners, rollover, jackpot_claimed = _distribute_prizes(
                draw.id, numbers, draw.prize_pool_total, draw.jackpot_rollover)
            draw.jackpot_claimed  = jackpot_claimed
            draw.jackpot_rollover = rollover
            draw.save(update_fields=['jackpot_claimed', 'jackpot_rollover'])

        return JsonResponse({'status': True, 'message': 'Draw published successfully',
                             'data': {'draw_id': draw.id, 'winning_numbers': numbers,
                                      'winners': winners, 'jackpot_claimed': jackpot_claimed,
                                      'jackpot_rollover': str(rollover)}})
    except Draw.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Draw not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── View / List Draws ─────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@jwt_required
def view_draw(request):
    try:
        data    = json.loads(request.body)
        draw_id = data.get('id')
        draw    = Draw.objects.get(id=draw_id, soft_delete=False)
        return JsonResponse({'status': True, 'data': {
            'draw_id': draw.id, 'title': draw.title, 'draw_type': draw.draw_type,
            'status': draw.status, 'draw_month': draw.draw_month, 'draw_year': draw.draw_year,
            'winning_numbers': draw.winning_numbers, 'prize_pool_total': str(draw.prize_pool_total),
            'jackpot_rollover': str(draw.jackpot_rollover), 'jackpot_claimed': draw.jackpot_claimed,
            'published_at': str(draw.published_at) if draw.published_at else None,
        }})
    except Draw.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Draw not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@jwt_required
def list_draws(request):
    try:
        data   = json.loads(request.body) if request.method == 'POST' else {}
        page   = int(data.get('page', 1))
        limit  = int(data.get('limit', 10))
        status = data.get('status', '')

        qs = Draw.objects.filter(soft_delete=False).order_by('-draw_year', '-draw_month')
        if status: qs = qs.filter(status=status)

        total = qs.count()
        draws = qs[(page - 1) * limit: page * limit]
        return JsonResponse({'status': True, 'current_page': page,
                             'total_pages': (total + limit - 1) // limit, 'total': total,
                             'data': [{'draw_id': d.id, 'title': d.title, 'draw_type': d.draw_type,
                                       'status': d.status, 'draw_month': d.draw_month,
                                       'draw_year': d.draw_year, 'winning_numbers': d.winning_numbers,
                                       'prize_pool_total': str(d.prize_pool_total),
                                       'jackpot_claimed': d.jackpot_claimed,
                                       'published_at': str(d.published_at) if d.published_at else None,
                                       } for d in draws]})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)
