# store/mixins.py
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(
            self.request, 
            'No tienes permisos para acceder a esta sección.'
        )
        return redirect('index')

# store/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        messages.error(
            request, 
            'No tienes permisos para acceder a esta sección.'
        )
        return redirect('index')
    return _wrapped_view

def anonymous_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(
                request, 
                'Ya has iniciado sesión.'
            )
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view