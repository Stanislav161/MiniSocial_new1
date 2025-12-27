# social_network/middleware.py
from django.http import HttpResponseRedirect
from django.shortcuts import redirect


class FixRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Блокируем пользователя 'admin' от случайного доступа к Django Admin
        if (request.user.is_authenticated and
                request.user.username == 'admin' and
                request.path.startswith('/admin/')):
            return redirect('/')

        # superadmin имеет полный доступ
        return self.get_response(request)