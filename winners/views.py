import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone

from authentication.utils import jwt_required, admin_required
from .models import WinnerVerification
from draws.models import DrawWinner


def _v_dict(v):
    return {
        'verification_id': v.id, 'user_id': v.user_id, 'draw_id': v.draw_id,
        'match_type': v.match_type, 'prize_amount': str(v.prize_amount),
        'proof_file': v.proof_file.name if v.proof_file else None,
        'proof_notes': v.proof_notes, 'status': v.status,
        'payment_status': v.payment_status, 'rejection_note': v.rejection_note,
        'reviewed_at': str(v.reviewed_at) if v.reviewed_at else None,
        'created_at': str(v.created_at),
    }


@csrf_exempt
@require_http_methods(['POST'])
@jwt_required
def submit_proof(request):
    try:
        user       = request.auth_user
        draw_id    = request.POST.get('draw_id')
        proof_file = request.FILES.get('proof_file')
        errors = {}
        if not draw_id:    errors['draw_id']    = 'Draw ID is required'
        if not proof_file: errors['proof_file'] = 'Proof file is required'
        if errors:
            return JsonResponse({'status': False, 'errors': errors}, status=200)

        winner = DrawWinner.objects.filter(draw_id=draw_id, user_id=user.id).first()
        if not winner:
            return JsonResponse({'status': False, 'error': 'You are not a winner of this draw'}, status=200)
        if WinnerVerification.objects.filter(user_id=user.id, draw_id=draw_id, soft_delete=False).exists():
            return JsonResponse({'status': False, 'error': 'Proof already submitted for this draw'}, status=200)

        v = WinnerVerification.objects.create(
            user_id=user.id, draw_id=draw_id, draw_winner_id=winner.id,
            match_type=winner.match_type, prize_amount=winner.prize_amount,
            proof_file=proof_file, proof_notes=request.POST.get('proof_notes', ''),
        )
        return JsonResponse({'status': True, 'message': 'Proof submitted. Awaiting admin review.',
                             'data': _v_dict(v)}, status=201)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@jwt_required
def view_verification(request):
    try:
        user = request.auth_user
        vs   = WinnerVerification.objects.filter(user_id=user.id, soft_delete=False).order_by('-id')
        return JsonResponse({'status': True, 'data': [_v_dict(v) for v in vs]})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def list_verifications(request):
    try:
        data   = json.loads(request.body)
        page   = int(data.get('page', 1))
        limit  = int(data.get('limit', 10))
        status = data.get('status', '')

        qs = WinnerVerification.objects.filter(soft_delete=False).order_by('-id')
        if status: qs = qs.filter(status=status)

        total = qs.count()
        vs    = qs[(page - 1) * limit: page * limit]
        return JsonResponse({'status': True, 'current_page': page,
                             'total_pages': (total + limit - 1) // limit,
                             'total': total, 'data': [_v_dict(v) for v in vs]})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def approve_verification(request):
    try:
        data  = json.loads(request.body)
        admin = request.auth_user
        v     = WinnerVerification.objects.get(id=data.get('id'), soft_delete=False)
        if v.status != 'pending':
            return JsonResponse({'status': False, 'error': f'Already {v.status}'}, status=200)
        v.status = 'approved'; v.reviewed_by = admin.id
        v.reviewed_at = timezone.now(); v.updated_at = timezone.now()
        v.save()
        return JsonResponse({'status': True, 'message': 'Approved', 'data': _v_dict(v)})
    except WinnerVerification.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Verification not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def reject_verification(request):
    try:
        data  = json.loads(request.body)
        admin = request.auth_user
        note  = data.get('rejection_note', '')
        if not note:
            return JsonResponse({'status': False, 'error': 'Rejection note required'}, status=200)
        v = WinnerVerification.objects.get(id=data.get('id'), soft_delete=False)
        v.status = 'rejected'; v.rejection_note = note
        v.reviewed_by = admin.id; v.reviewed_at = timezone.now(); v.updated_at = timezone.now()
        v.save()
        return JsonResponse({'status': True, 'message': 'Rejected', 'data': _v_dict(v)})
    except WinnerVerification.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Verification not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def mark_payout_paid(request):
    try:
        data = json.loads(request.body)
        v    = WinnerVerification.objects.get(id=data.get('id'), soft_delete=False, status='approved')
        v.payment_status = 'paid'; v.updated_at = timezone.now()
        v.save(update_fields=['payment_status', 'updated_at'])
        return JsonResponse({'status': True, 'message': 'Payout marked as paid', 'data': _v_dict(v)})
    except WinnerVerification.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Verification not found or not approved'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)
