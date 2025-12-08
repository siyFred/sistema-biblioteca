from rest_framework import permissions

class IsLibrarianOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada:
    - Leitores: Apenas Leitura (GET)
    - Bibliotecários/Admins: Leitura e Escrita (POST, PUT, DELETE)
    """

    def has_permission(self, request, view):
        # 1. Se o método for seguro (GET, HEAD, OPTIONS), libera geral.
        if request.method in permissions.SAFE_METHODS:
            return True

        # 2. Se for escrita (POST/PUT/DELETE), verifica o crachá.
        # O usuário precisa estar logado E ser Bibliotecário ou Superusuário.
        return request.user.is_authenticated and (
            request.user.role == 'LIBRARIAN' or request.user.is_staff
        )