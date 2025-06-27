from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Allow safe methods for everyone, other actions — only for admins
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # GET, HEAD, OPTIONS — allowed for everyone
        return request.user and request.user.is_authenticated and request.user.is_staff
