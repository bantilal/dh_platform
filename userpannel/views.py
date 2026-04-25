from django.shortcuts import render


def home(request):
    return render(request, 'index.html')


def login_page(request):
    return render(request, 'auth/login.html')


def register_page(request):
    return render(request, 'auth/register.html')


def user_dashboard(request):
    return render(request, 'user/dashboard.html')


def user_scores(request):
    return render(request, 'user/scores.html')


def user_draws(request):
    return render(request, 'user/draws.html')


def user_charity(request):
    return render(request, 'user/charity.html')


def user_subscription(request):
    return render(request, 'user/subscription.html')


def user_winnings(request):
    return render(request, 'user/winnings.html')


def admin_dashboard(request):
    return render(request, 'admin_panel/dashboard.html')


def admin_users(request):
    return render(request, 'admin_panel/users.html')


def admin_draws(request):
    return render(request, 'admin_panel/draws.html')


def admin_charities(request):
    return render(request, 'admin_panel/charities.html')


def admin_winners(request):
    return render(request, 'admin_panel/winners.html')
