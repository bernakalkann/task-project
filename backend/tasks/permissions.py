from rest_framework import permissions

class IsCommentOwnerOrAdmin(permissions.BasePermission):
    """
    Yorumların sadece sahibi veya adminler tarafından düzenlenebilmesini/silinebilmesini sağlar.
    Diğer kullanıcılar sadece okuma yapabilir.
    """
    def has_object_permission(self, request, view, obj):
        # GET, HEAD veya OPTIONS gibi güvenli metotlara izin ver
        if request.method in permissions.SAFE_METHODS:
            return True

        # Düzenleme veya silme işlemi için yorumun sahibi veya admin olmalı
        return obj.user == request.user or (request.user and request.user.is_staff)
