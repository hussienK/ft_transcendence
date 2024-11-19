from rest_framework.permissions import BasePermission
from rest_framework.authentication import SessionAuthentication

#a custom permission to only allow certain stuff if user has required roles

#email verified
class IsVerified(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified
    
# 2FA enabled
class IsTwoFactorAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified and request.user.two_factor_enabled


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Skip CSRF check