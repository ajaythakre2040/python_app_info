from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import User
from ..permissions.authentication import LoginTokenAuthentication
from ..serializer import DomainSerializer
from ..utils.pagination import CustomPagination
from rest_framework.permissions import IsAuthenticated

#=============================Total User history=======================#
class TotalUserHistoryAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [LoginTokenAuthentication]
    serializer_class = DomainSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return User.objects.filter(deleted_at__isnull=True).order_by('created_at')
    
 #=============================Active User History======================#
class ActiveUserListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [LoginTokenAuthentication]
    serializer_class = DomainSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # Fetch only already active users
        return User.objects.filter(is_active=True, deleted_at__isnull=True).order_by('created_at')

#=============================Deactive User History======================#
class DeactiveUserListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [LoginTokenAuthentication]
    serializer_class = DomainSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # Fetch only already inactive users
        return User.objects.filter(is_active=False, deleted_at__isnull=True).order_by('created_at')