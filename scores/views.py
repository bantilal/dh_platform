import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction

from authentication.utils import jwt_required, admin_required, subscriber_required
from .models import GolfScore

MAX_SCORES = 5


def _score_dict(s):
    return {
        'score_id':   s.id,
        'score':      s.score,
        'score_date': str(s.score_date),
        'notes':      s.notes,
        'created_at': str(s.created_at),
        'updated_at': str(s.updated_at),
    }


@csrf_exempt
@require_http_methods(['POST'])
@subscriber_required
def add_score(request):
    try:
        data       = json.loads(request.body)
        user       = request.auth_user
        score_val  = data.get('score')
        score_date = data.get('score_date')
        notes      = data.get('notes', '')

        errors = {}
        if score_val is None:
            errors['score'] = 'Score is required'
        elif not (1 <= int(score_val) <= 45):
            errors['score'] = 'Score must be between 1 and 45 (Stableford)'
        if not score_date:
            errors['score_date'] = 'Score date is required'
        if errors:
            return JsonResponse({'status': False, 'errors': errors}, status=200)

        with transaction.atomic():
            if GolfScore.objects.filter(user_id=user.id, score_date=score_date, soft_delete=False).exists():
                return JsonResponse({'status': False,
                                     'error': 'A score already exists for this date. Edit or delete the existing entry.'}, status=200)

            existing = GolfScore.objects.filter(user_id=user.id, soft_delete=False).order_by('score_date')
            if existing.count() >= MAX_SCORES:
                oldest = existing.first()
                oldest.soft_delete = True
                oldest.save(update_fields=['soft_delete'])

            new_score = GolfScore.objects.create(
                user_id=user.id, score=int(score_val),
                score_date=score_date, notes=notes,
            )

        return JsonResponse({'status': True, 'message': 'Score added successfully',
                             'data': _score_dict(new_score)}, status=201)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@subscriber_required
def edit_score(request):
    try:
        data     = json.loads(request.body)
        user     = request.auth_user
        score_id = data.get('id')
        errors   = {}

        if not score_id:
            errors['id'] = 'Score ID is required'
        score_val = data.get('score')
        if score_val is not None and not (1 <= int(score_val) <= 45):
            errors['score'] = 'Score must be between 1 and 45'
        if errors:
            return JsonResponse({'status': False, 'errors': errors}, status=200)

        score = GolfScore.objects.get(id=score_id, user_id=user.id, soft_delete=False)

        if score_val is not None:
            score.score = int(score_val)
        if 'notes' in data:
            score.notes = data['notes']
        if 'score_date' in data:
            new_date = data['score_date']
            if GolfScore.objects.filter(user_id=user.id, score_date=new_date,
                                        soft_delete=False).exclude(id=score_id).exists():
                return JsonResponse({'status': False,
                                     'error': 'Another score already exists for that date'}, status=200)
            score.score_date = new_date

        score.updated_at = timezone.now()
        score.save()
        return JsonResponse({'status': True, 'message': 'Score updated successfully',
                             'data': _score_dict(score)})
    except GolfScore.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Score not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@subscriber_required
def delete_score(request):
    try:
        data     = json.loads(request.body)
        user     = request.auth_user
        score_id = data.get('id')
        if not score_id:
            return JsonResponse({'status': False, 'error': 'Score ID is required'}, status=200)

        score = GolfScore.objects.get(id=score_id, user_id=user.id, soft_delete=False)
        score.soft_delete = True
        score.save(update_fields=['soft_delete'])
        return JsonResponse({'status': True, 'message': 'Score deleted successfully'})
    except GolfScore.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Score not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@jwt_required
def list_scores(request):
    try:
        user    = request.auth_user
        data    = json.loads(request.body) if request.method == 'POST' else {}
        user_id = int(data.get('user_id', user.id))
        if user.role != 'admin':
            user_id = user.id

        scores = GolfScore.objects.filter(
            user_id=user_id, soft_delete=False
        ).order_by('-score_date')[:MAX_SCORES]

        return JsonResponse({'status': True, 'data': [_score_dict(s) for s in scores]})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def admin_edit_score(request):
    try:
        data      = json.loads(request.body)
        score_id  = data.get('id')
        score_val = data.get('score')
        if not score_id:
            return JsonResponse({'status': False, 'error': 'Score ID required'}, status=200)
        score = GolfScore.objects.get(id=score_id, soft_delete=False)
        if score_val is not None:
            if not (1 <= int(score_val) <= 45):
                return JsonResponse({'status': False, 'error': 'Score must be 1–45'}, status=200)
            score.score = int(score_val)
        if 'notes' in data:
            score.notes = data['notes']
        score.updated_at = timezone.now()
        score.save()
        return JsonResponse({'status': True, 'message': 'Score updated by admin',
                             'data': _score_dict(score)})
    except GolfScore.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Score not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)
