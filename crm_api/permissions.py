from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'MANAGER']

class IsSalesPerson(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SALES'

class IsAssignedSalesOrManager(permissions.BasePermission):
    """
    Allows Managers/Admins full access.
    Sales Executives only have access if the lead is assigned to them.
    """
    def has_object_permission(self, request, view, obj):
        # Admins and Managers can see everything
        if request.user.role in ['ADMIN', 'MANAGER']:
            return True
        
        # Lead object permission
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
            
        # Related objects (Meeting, Quotation etc) permission
        if hasattr(obj, 'lead'):
            return obj.lead.assigned_to == request.user
            
        return False
