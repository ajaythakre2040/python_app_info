from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from ..models import User
from ..models.password_history import Password_History
from ..serializer.user import UserSerializer
from ..permissions.authentication import LoginTokenAuthentication
# from ..utils.status import update_user_status
from ..utils.pagination import CustomPagination
from ..utils.password import validate_custom_password, is_password_reused

class UserAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]

    # ================= GET / GET BY ID =================#
    def get(self, request, id=None):
        try:
            queryset = User.objects.filter(deleted_at__isnull=True).order_by("-created_at")

            # # Update all users' status dynamically
            # for user in queryset:
            #     update_user_status(user)

            if id:
                # Return single user by ID
                user = get_object_or_404(queryset, id=id)
                serializer = UserSerializer(user)
                return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

            # Paginate all users (active + inactive)
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset.order_by("-created_at"), request, view=self)
            serializer = UserSerializer(paginated_queryset, many=True)

            # Count active and inactive users
            active_count = queryset.filter(is_active=True).count()
            inactive_count = queryset.filter(is_active=False).count()

            response_data = {
                "total_records": queryset.count(),
                "total_pages": paginator.page.paginator.num_pages,
                "current_page": paginator.page.number,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "active_count": active_count,
                "inactive_count": inactive_count,
                "results": serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Something went wrong: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ================= POST CREATE =================#
    def post(self, request):
        data = request.data.copy()
        password = data.get("password")
        if not password:
            return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data["password"] = validate_custom_password(password)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save(
                password=make_password(data["password"]),
                created_by=request.user,
                updated_by=request.user,
                is_active=True
            )
            # Save password in history
            Password_History.objects.create(user=user, password=user.password)

            return Response({"success": True, "message": "User created successfully", "data": serializer.data},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ================= PATCH UPDATE =================#
    def patch(self, request, id):
        user = get_object_or_404(User, id=id, deleted_at__isnull=True)
        data = request.data.copy()

        if "password" in data and not data["password"]:
            data.pop("password")

        serializer = UserSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save(updated_by=request.user)

            return Response(
            {"success": True, "message": "User updated successfully"},
            status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ================= DELETE USER =================#
    def delete(self, request, id):
        user = get_object_or_404(User, id=id, deleted_at__isnull=True, is_active=True)
        user.deleted_at = timezone.now()
        user.deleted_by = request.user
        user.is_active = False
        user.updated_by = request.user
        user.updated_at = timezone.now()
        user.save()
        return Response({"success": True, "message": "User deleted successfully"}, status=status.HTTP_200_OK)