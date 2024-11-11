from rest_framework.permissions import BasePermission

class IsAdminOrSeller(BasePermission):
    """
    Custom permission to only allow admin or seller users to edit or delete.
    """

    def has_permission(self, request, view):
        # Allow access if the user is authenticated and has the role of 'admin' or 'seller'
        if request.user and request.user.is_authenticated:
            return request.user.role in ['Admin', 'Seller']  # Assuming user has a `role` field
        return False