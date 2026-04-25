
import random
import string
from functools import wraps
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

def _extract_user(request):
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None, 'Authorization token missing or invalid format'
    try:
        token   = AccessToken(auth.split(' ')[1])
        user_id = token['user_id']
        return User.objects.get(id=user_id, is_active=True, soft_delete=False), None
    except User.DoesNotExist:
        return None, 'User not found or disabled'
    except Exception:
        return None, 'Invalid or expired token'


def jwt_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user, err = _extract_user(request)
        if err:
            return JsonResponse({'status': False, 'error': err}, status=401)
        request.auth_user = user
        return func(request, *args, **kwargs)
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user, err = _extract_user(request)
        if err:
            return JsonResponse({'status': False, 'error': err}, status=401)
        if user.role != 'admin':
            return JsonResponse({'status': False, 'error': 'Admin access required'}, status=403)
        request.auth_user = user
        return func(request, *args, **kwargs)
    return wrapper


def subscriber_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        from subscriptions.models import Subscription
        from django.utils import timezone
        user, err = _extract_user(request)
        if err:
            return JsonResponse({'status': False, 'error': err}, status=401)
        if user.role != 'admin':
            active = Subscription.objects.filter(
                user_id=user.id, status='active',
                end_date__gte=timezone.now().date()
            ).exists()
            if not active:
                return JsonResponse({'status': False, 'error': 'Active subscription required'}, status=403)
        request.auth_user = user
        return func(request, *args, **kwargs)
    return wrapper


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


def generate_username(email):
    base = email.split('@')[0]
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{base}_{suffix}"