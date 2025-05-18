from rest_framework import permissions


class IsCustomerOrAdmin(permissions.BasePermission):
    """
    Only customers or admin users can access this resource.
    """

    def has_permission(self, request, view):
        """
        Global permission check for list and create actions.
        Allows only authenticated customers or admins.

        params:
            request: The HTTP request object.
            view: The view that is being accessed.
        returns:
            bool: True if the user has permission, False otherwise.
        """
        user_profile = getattr(request.user, 'profile', None)
        return (
            request.user.is_authenticated and 
            user_profile and 
            (user_profile.type == 'customer' or request.user.is_staff)
        )

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check for update/delete actions.
        Allows safe methods for all users.
        Allows modification only if the user is the customer or an admin.

        params:
            request: The HTTP request object.
            view: The view that is being accessed.
            obj: The object to check permissions against.
        returns:
            bool: True if the user has permission, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.customer_user == request.user or request.user.is_staff


    