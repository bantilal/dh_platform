from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count
import json

from authentication.utils import jwt_required, admin_required


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@jwt_required
def user_dashboard(request):
    try:
        from authentication.models import User
        from subscriptions.models import Subscription
        from scores.models import GolfScore
        from charities.models import Charity
        from draws.models import Draw, DrawWinner, DrawParticipant
        from winners.models import WinnerVerification

        user = request.auth_user
        now  = timezone.now().date()

        sub = Subscription.objects.filter(user_id=user.id, soft_delete=False).order_by('-id').first()
        sub_data = None
        if sub:
            sub_data = {
                'plan': sub.plan, 'status': sub.status, 'amount': str(sub.amount),
                'end_date': str(sub.end_date), 'renewal_date': str(sub.renewal_date),
                'auto_renew': sub.auto_renew,
                'is_active': sub.status == 'active' and sub.end_date >= now,
                'charity_percent': str(sub.charity_percent),
                'charity_amount': str(sub.charity_amount),
            }

        scores = GolfScore.objects.filter(user_id=user.id, soft_delete=False).order_by('-score_date')[:5]
        scores_data = [{'score_id': s.id, 'score': s.score, 'score_date': str(s.score_date)} for s in scores]

        charity_data = None
        if user.charity_id:
            try:
                c = Charity.objects.get(id=user.charity_id, soft_delete=False)
                charity_data = {'charity_id': c.id, 'name': c.name,
                                'logo': c.logo.name if c.logo else None,
                                'my_percent': str(user.charity_percent)}
            except Charity.DoesNotExist:
                pass

        participated = DrawParticipant.objects.filter(user_id=user.id).count()
        latest_draw  = Draw.objects.filter(status='published').order_by('-draw_year', '-draw_month').first()
        upcoming     = Draw.objects.filter(status__in=['draft', 'simulated']).order_by('draw_year', 'draw_month').first()

        total_won = DrawWinner.objects.filter(user_id=user.id).aggregate(t=Sum('prize_amount'))['t'] or Decimal('0')
        pending_payment = WinnerVerification.objects.filter(
            user_id=user.id, status='approved', payment_status='pending'
        ).aggregate(t=Sum('prize_amount'))['t'] or Decimal('0')

        wins = DrawWinner.objects.filter(user_id=user.id).order_by('-id')[:5]
        wins_list = [{'draw_id': w.draw_id, 'match_type': w.match_type,
                      'prize_amount': str(w.prize_amount), 'created_at': str(w.created_at)} for w in wins]

        return JsonResponse({'status': True, 'data': {
            'user': {'user_id': user.id, 'first_name': user.first_name,
                     'last_name': user.last_name, 'email': user.email, 'role': user.role},
            'subscription': sub_data,
            'scores': scores_data,
            'charity': charity_data,
            'draws': {
                'total_participated': participated,
                'latest_draw': {'draw_id': latest_draw.id, 'title': latest_draw.title,
                                'winning_numbers': latest_draw.winning_numbers,
                                'draw_month': latest_draw.draw_month,
                                'draw_year': latest_draw.draw_year} if latest_draw else None,
                'upcoming_draw': {'draw_id': upcoming.id, 'title': upcoming.title,
                                   'draw_month': upcoming.draw_month,
                                   'draw_year': upcoming.draw_year} if upcoming else None,
            },
            'winnings': {'total_won': str(total_won), 'pending_payment': str(pending_payment),
                         'recent_wins': wins_list},
        }})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@admin_required
def admin_dashboard(request):
    try:
        from authentication.models import User
        from subscriptions.models import Subscription
        from draws.models import Draw, DrawWinner
        from charities.models import Charity
        from winners.models import WinnerVerification

        now = timezone.now()
        today = now.date()

        total_users  = User.objects.filter(soft_delete=False).count()
        active_users = User.objects.filter(soft_delete=False, is_active=True).count()
        new_month    = User.objects.filter(soft_delete=False,
                                           created_at__month=now.month, created_at__year=now.year).count()

        active_subs   = Subscription.objects.filter(status='active', end_date__gte=today)
        monthly_subs  = active_subs.filter(plan='monthly').count()
        yearly_subs   = active_subs.filter(plan='yearly').count()
        total_revenue = Subscription.objects.filter(status='active').aggregate(t=Sum('amount'))['t'] or Decimal('0')
        prize_pool    = active_subs.aggregate(t=Sum('prize_pool_amount'))['t'] or Decimal('0')
        charity_pool  = active_subs.aggregate(t=Sum('charity_amount'))['t'] or Decimal('0')

        latest_draw = Draw.objects.filter(status='published').order_by('-draw_year', '-draw_month').first()
        pending_v   = WinnerVerification.objects.filter(status='pending', soft_delete=False).count()
        pending_p   = WinnerVerification.objects.filter(status='approved', payment_status='pending', soft_delete=False).count()
        total_charities = Charity.objects.filter(soft_delete=False, status=True).count()
        total_received  = Charity.objects.filter(soft_delete=False).aggregate(t=Sum('total_received'))['t'] or Decimal('0')

        return JsonResponse({'status': True, 'data': {
            'users': {'total': total_users, 'active': active_users, 'new_this_month': new_month},
            'subscriptions': {'active_total': active_subs.count(), 'monthly': monthly_subs,
                              'yearly': yearly_subs, 'total_revenue': str(total_revenue)},
            'prize_pool': {'total': str(prize_pool), 'charity_pool': str(charity_pool),
                           'pool_5_match': str((prize_pool * Decimal('0.40')).quantize(Decimal('0.01'))),
                           'pool_4_match': str((prize_pool * Decimal('0.35')).quantize(Decimal('0.01'))),
                           'pool_3_match': str((prize_pool * Decimal('0.25')).quantize(Decimal('0.01')))},
            'draws': {'latest': {'draw_id': latest_draw.id, 'title': latest_draw.title,
                                  'winning_numbers': latest_draw.winning_numbers,
                                  'jackpot_claimed': latest_draw.jackpot_claimed} if latest_draw else None,
                      'total': Draw.objects.filter(soft_delete=False).count(),
                      'published': Draw.objects.filter(status='published').count()},
            'charities': {'total': total_charities, 'total_received': str(total_received)},
            'winners': {'pending_verifications': pending_v, 'pending_payouts': pending_p},
        }})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def admin_reports(request):
    try:
        data        = json.loads(request.body)
        report_type = data.get('report_type', 'overview')

        from subscriptions.models import Subscription
        from draws.models import Draw, DrawParticipant, DrawWinner
        from charities.models import Charity
        from django.db.models.functions import TruncMonth

        if report_type == 'subscriptions_by_month':
            result = Subscription.objects.annotate(month=TruncMonth('created_at')) \
                .values('month', 'plan').annotate(count=Count('id'), revenue=Sum('amount')).order_by('month')
            report = [{'month': str(r['month']), 'plan': r['plan'],
                       'count': r['count'], 'revenue': str(r['revenue'])} for r in result]

        elif report_type == 'draw_statistics':
            draws = Draw.objects.filter(status='published').order_by('-draw_year', '-draw_month')
            report = [{'draw_id': d.id, 'title': d.title, 'draw_month': d.draw_month,
                       'draw_year': d.draw_year, 'prize_pool': str(d.prize_pool_total),
                       'participants': DrawParticipant.objects.filter(draw_id=d.id).count(),
                       'winners': DrawWinner.objects.filter(draw_id=d.id).count()} for d in draws]

        elif report_type == 'charity_contributions':
            report = [{'charity_id': c.id, 'name': c.name, 'total_received': str(c.total_received)}
                      for c in Charity.objects.filter(soft_delete=False).order_by('-total_received')]
        else:
            report = {}

        return JsonResponse({'status': True, 'report_type': report_type, 'data': report})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)
