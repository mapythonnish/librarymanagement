from rest_framework.permissions import BasePermission


class IsLibrarian(BasePermission):
    """
    Custom permission to allow access only to librarian users.
    """
    message = "You do not have the necessary permissions to access this view."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_librarian
