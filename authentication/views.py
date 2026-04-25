import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import generate_username

from .utils import jwt_required, admin_required, get_tokens

User = get_user_model()


@csrf_exempt
@require_http_methods(['POST'])
def register_view(request):
    try:
        data = json.loads(request.body)

        first_name   = data.get('first_name', '').strip()
        last_name    = data.get('last_name', '').strip()
        email        = data.get('email', '').strip().lower()
        password     = data.get('password', '')
        contact_no   = data.get('contact_no', '')
        country_code = data.get('country_code', '+44')
        charity_id   = data.get('charity_id')
        charity_pct  = float(data.get('charity_percent', 10))

        errors = {}

        if not first_name:
            errors['first_name'] = 'First name is required'

        if not email:
            errors['email'] = 'Email is required'

        if not password or len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters'

        if charity_pct < 10:
            errors['charity_percent'] = 'Minimum 10% required'

        if User.objects.filter(email=email).exists():
            errors['email'] = 'Email already registered'

        if errors:
            return JsonResponse({'status': False, 'errors': errors}, status=200)

        # 🔥 Auto username
        username = generate_username(email)

        user = User.objects.create_user(
            username=username,   # 👈 added
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            contact_no=contact_no,
            country_code=country_code,
            charity_id=charity_id,
            charity_percent=charity_pct,
            role='public',
        )

        tokens = get_tokens(user)

        return JsonResponse({
            'status': True,
            'message': 'Registration successful',
            'data': {
                'user_id': user.id,
                'first_name': user.first_name,
                'email': user.email,
                'role': user.role,
                'tokens': tokens,
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── Login ─────────────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
def login_view(request):
    try:
        data     = json.loads(request.body)
        email    = data.get('email', '').strip().lower()
        password = data.get('password', '')

        errors = {}
        if not email:    errors['email']    = 'Email is required'
        if not password: errors['password'] = 'Password is required'
        if errors:
            return JsonResponse({'status': False, 'errors': errors}, status=200)

        try:
            user = User.objects.get(email=email, soft_delete=False)
        except User.DoesNotExist:
            return JsonResponse({'status': False, 'error': 'Invalid email or password'}, status=200)

        if not user.check_password(password):
            return JsonResponse({'status': False, 'error': 'Invalid email or password'}, status=200)
        if not user.is_active:
            return JsonResponse({'status': False, 'error': 'Account is disabled. Contact support.'}, status=200)

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        tokens = get_tokens(user)
        return JsonResponse({
            'status': True, 'message': 'Login successful',
            'data': {
                'user_id': user.id, 'first_name': user.first_name,
                'last_name': user.last_name, 'email': user.email,
                'role': user.role, 'tokens': tokens,
            }
        }, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── Check Auth ────────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['GET', 'POST'])
@jwt_required
def check_auth_view(request):
    u = request.auth_user
    return JsonResponse({'status': True, 'data': {
        'user_id': u.id, 'first_name': u.first_name, 'last_name': u.last_name,
        'email': u.email, 'role': u.role,
        'charity_id': u.charity_id, 'charity_percent': str(u.charity_percent),
    }})


# ── Logout ────────────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@jwt_required
def logout_view(request):
    try:
        data    = json.loads(request.body)
        refresh = data.get('refresh')
        if refresh:
            RefreshToken(refresh).blacklist()
        return JsonResponse({'status': True, 'message': 'Logged out successfully'})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── Add User (Admin) ──────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def add_user_view(request):
    try:
        data = json.loads(request.body)
        errors = {}
        email      = data.get('email', '').strip().lower()
        first_name = data.get('first_name', '').strip()
        last_name  = data.get('last_name', '').strip()
        role       = data.get('role', 'public')
        password   = data.get('password', 'DigitalHeroes@2026')

        if not email:      errors['email']      = 'Email required'
        if not first_name: errors['first_name'] = 'First name required'
        if User.objects.filter(email=email).exists():
            errors['email'] = 'Email already exists'
        if errors:
            return JsonResponse({'status': False, 'errors': errors}, status=200)

        user = User.objects.create_user(
            email=email, password=password,
            first_name=first_name, last_name=last_name, role=role,
        )
        return JsonResponse({'status': True, 'message': 'User created',
                             'data': {'user_id': user.id, 'email': user.email, 'role': user.role}}, status=201)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── View User ─────────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def view_user(request):
    try:
        data    = json.loads(request.body)
        user_id = data.get('id')
        if not user_id:
            return JsonResponse({'status': False, 'error': 'User ID required'}, status=200)
        u = User.objects.get(id=user_id, soft_delete=False)
        return JsonResponse({'status': True, 'data': {
            'user_id': u.id, 'first_name': u.first_name, 'last_name': u.last_name,
            'email': u.email, 'contact_no': u.contact_no, 'country_code': u.country_code,
            'role': u.role, 'charity_id': u.charity_id, 'charity_percent': str(u.charity_percent),
            'is_active': u.is_active, 'created_at': str(u.created_at),
            'profile_image': u.profile_image.name if u.profile_image else None,
        }})
    except User.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'User not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── User List (Admin) ─────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def list_users(request):
    try:
        data   = json.loads(request.body)
        page   = int(data.get('page', 1))
        limit  = int(data.get('limit', 10))
        search = data.get('search', '').strip()
        role   = data.get('role', '')

        qs = User.objects.filter(soft_delete=False).order_by('-id')
        if search: qs = qs.filter(email__icontains=search) | User.objects.filter(first_name__icontains=search, soft_delete=False)
        if role:   qs = qs.filter(role=role)

        total  = qs.count()
        offset = (page - 1) * limit
        users  = qs[offset: offset + limit]
        data_list = [{'user_id': u.id, 'first_name': u.first_name, 'last_name': u.last_name,
                      'email': u.email, 'role': u.role, 'is_active': u.is_active,
                      'created_at': str(u.created_at)} for u in users]
        return JsonResponse({'status': True, 'current_page': page,
                             'total_pages': (total + limit - 1) // limit,
                             'total_users': total, 'data': data_list})
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── Edit User ─────────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@jwt_required
def edit_user(request):
    try:
        data    = json.loads(request.body)
        user    = request.auth_user
        user_id = int(data.get('id', user.id))
        if user.role != 'admin':
            user_id = user.id
        target = User.objects.get(id=user_id, soft_delete=False)
        for field in ('first_name', 'last_name', 'contact_no', 'country_code', 'charity_id'):
            if field in data: setattr(target, field, data[field])
        if 'charity_percent' in data:
            pct = float(data['charity_percent'])
            if pct < 10:
                return JsonResponse({'status': False, 'error': 'Minimum 10% charity required'}, status=200)
            target.charity_percent = pct
        target.updated_at = timezone.now()
        target.save()
        return JsonResponse({'status': True, 'message': 'User updated successfully'})
    except User.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'User not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)


# ── User Status Toggle (Admin) ────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
@admin_required
def user_status(request):
    try:
        data    = json.loads(request.body)
        user_id = data.get('id')
        if not user_id:
            return JsonResponse({'status': False, 'error': 'User ID required'}, status=200)
        u = User.objects.get(id=user_id, soft_delete=False)
        u.is_active = not u.is_active
        u.save(update_fields=['is_active'])
        return JsonResponse({'status': True,
                             'message': f"User {'activated' if u.is_active else 'deactivated'}",
                             'data': {'user_id': u.id, 'is_active': u.is_active}})
    except User.DoesNotExist:
        return JsonResponse({'status': False, 'error': 'User not found'}, status=200)
    except Exception as e:
        return JsonResponse({'status': False, 'error': str(e)}, status=500)
