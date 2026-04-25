import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import F

from authentication.utils import jwt_required, admin_required
from .models import Charity, CharityEvent, CharityDonation


def _charity_dict(c):
    return {
        'charity_id':    c.id, 'name': c.name, 'description': c.description,
        'short_bio':     c.short_bio, 'website': c.website, 'category': c.category,
        'is_featured':   c.is_featured, 'status': c.status,
        'total_received': str(c.total_received),
        'logo':   c.logo.name if c.logo else None,
        'banner': c.banner.name if c.banner else None,
        'created_at': str(c.created_at),
    }


@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def add_charity(request):
    try:
        name        = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        errors = {}
        if not name:        errors['name']        = 'Charity name is required'
        if not description: errors['description'] = 'Description is required'
        if errors:
            return JsonResponse({'status': False, 'errors': errors}, status=200)

        charity = Charity.objects.create(
            name=name, description=description,
            short_bio=request.POST.get('short_bio', ''),
            website=request.POST.get('website', ''),
            category=request.POST.get('category', ''),
            is_featured=request.POST.get('is_featured', 'false').lower() == 'true',
            logo=request.FILES.get('logo'),
            banner=request.FILES.get('banner'),
        )
        return JsonResponse({'status': True, 'message': 'Charity added successfully',
                             'data': _charity_dict(charity)}, status=201)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def edit_charity(request):
    try:
        charity_id = request.POST.get('id')
        if not charity_id:
            return JsonResponse({'status': False, 'error': 'Charity ID required'}, status=200)
        charity = Charity.objects.get(id=charity_id, soft_delete=False)
        for f in ('name', 'description', 'short_bio', 'website', 'category'):
            if f in request.POST: setattr(charity, f, request.POST[f])
        if 'is_featured' in request.POST:
            charity.is_featured = request.POST['is_featured'].lower() == 'true'
        if 'logo'   in request.FILES: charity.logo   = request.FILES['logo']
        if 'banner' in request.FILES: charity.banner = request.FILES['banner']
        charity.updated_at = timezone.now()
        charity.save()
        return JsonResponse({'status': True, 'message': 'Charity updated', 'data': _charity_dict(charity)})
    except Charity.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Charity not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def delete_charity(request):
    try:
        data = json.loads(request.body)
        c    = Charity.objects.get(id=data.get('id'), soft_delete=False)
        c.soft_delete = True
        c.save(update_fields=['soft_delete'])
        return JsonResponse({'status': True, 'message': 'Charity deleted'})
    except Charity.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Charity not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def view_charity(request):
    try:
        data       = json.loads(request.body) if request.method == 'POST' else {}
        charity_id = data.get('id') or request.GET.get('id')
        charity    = Charity.objects.get(id=charity_id, soft_delete=False, status=True)
        events     = CharityEvent.objects.filter(charity_id=charity_id, soft_delete=False).order_by('event_date')
        result     = _charity_dict(charity)
        result['events'] = [{'event_id': e.id, 'title': e.title,
                              'event_date': str(e.event_date), 'location': e.location,
                              'image': e.image.name if e.image else None} for e in events]
        return JsonResponse({'status': True, 'data': result})
    except Charity.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'Charity not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def list_charities(request):
    try:
        data     = json.loads(request.body) if request.method == 'POST' and request.body else {}
        page     = int(data.get('page', 1))
        limit    = int(data.get('limit', 12))
        search   = data.get('search', request.GET.get('search', '')).strip()
        category = data.get('category', request.GET.get('category', '')).strip()
        featured = data.get('is_featured', request.GET.get('is_featured'))

        qs = Charity.objects.filter(soft_delete=False, status=True).order_by('-is_featured', 'name')
        if search:   qs = qs.filter(name__icontains=search)
        if category: qs = qs.filter(category__icontains=category)
        if featured is not None:
            qs = qs.filter(is_featured=(str(featured).lower() in ('true', '1')))

        total = qs.count()
        charities = qs[(page - 1) * limit: page * limit]
        return JsonResponse({'status': True, 'current_page': page,
                             'total_pages': (total + limit - 1) // limit, 'total': total,
                             'data': [_charity_dict(c) for c in charities]})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@jwt_required
def donate_charity(request):
    try:
        data       = json.loads(request.body)
        user       = request.auth_user
        charity_id = data.get('charity_id')
        amount     = float(data.get('amount', 0))
        errors = {}
        if not charity_id: errors['charity_id'] = 'Charity ID required'
        if amount <= 0:    errors['amount']     = 'Amount must be > 0'
        if errors:
            return JsonResponse({'status': False, 'errors': errors}, status=200)

        Charity.objects.filter(id=charity_id).update(total_received=F('total_received') + amount)
        don = CharityDonation.objects.create(user_id=user.id, charity_id=charity_id, amount=amount)
        return JsonResponse({'status': True, 'message': 'Donation successful',
                             'data': {'donation_id': don.id, 'amount': str(don.amount)}}, status=201)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)
