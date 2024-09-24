from ninja_extra import permissions


class IsSuperAdmin(permissions.IsAuthenticated):
    def has_permission(self, request, controller):
        user = request.user
        return bool(super().has_permission(request, controller) and user.groups.filter(name='superadmin').exists())