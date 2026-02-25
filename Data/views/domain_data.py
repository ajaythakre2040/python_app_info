from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import User
from ..serializer import UserHistorySerializer
from ..utils.status import update_user_status
from ..utils.pagination import CustomPagination

#=============================Total User history=======================#
class TotalUserHistoryAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserHistorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return User.objects.all().order_by('created_at')
 #=============================Active User History======================#
class ActiveUserListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserHistorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        users = User.objects.filter(deleted_at__isnull=True)
        for user in users:
            update_user_status(user)
        return User.objects.filter(is_active=True, deleted_at__isnull=True).order_by('created_at')


#==============================Deactive User History==========================#
class DeactiveUserListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserHistorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        users = User.objects.filter(deleted_at__isnull=True)
        for user in users:
            update_user_status(user)
        return User.objects.filter(is_active=False, deleted_at__isnull=True).order_by('created_at')