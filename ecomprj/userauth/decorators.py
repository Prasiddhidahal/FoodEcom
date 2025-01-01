from django.http import HttpResponseForbidden

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Get the user's role, here assuming user role is stored as a list of groups
            user_groups = request.user.groups.values_list('name', flat=True)
            # Check if user belongs to the allowed groups
            if not any(role in user_groups for role in allowed_roles):
                return HttpResponseForbidden("You do not have permission to view this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
