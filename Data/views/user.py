from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from ..models import User
from ..serializer.user import UserSerializer
from ..utils.pagination import CustomPagination
from ..utils.password import validate_custom_password, is_password_reused
from ..permissions.authentication import LoginTokenAuthentication
from ..models.password_history import Password_History

class UserAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]

    # ================= GET / GET BY ID =================
    def get(self, request, id=None):
        try:
            if id:
                user = get_object_or_404(User, id=id, deleted_at__isnull=True, is_active=True)
                serializer = UserSerializer(user)
                return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

            queryset = User.objects.filter(deleted_at__isnull=True, is_active=True).order_by("-created_at")
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
            serializer = UserSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({"error": f"Something went wrong: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ================= POST CREATE =================
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
                is_active=True  # ensure user is active on creation
            )
            # Save password in history
            Password_History.objects.create(user=user, password=user.password)

            return Response({"success": True, "message": "User created successfully", "data": serializer.data},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ================= PATCH UPDATE =================
    def patch(self, request, id):
        user = get_object_or_404(User, id=id, deleted_at__isnull=True, is_active=True)
        data = request.data.copy()
        password = data.get("password")

        if password:
            try:
                # Validate password
                data["password"] = validate_custom_password(password)
                # Check password reuse
                if is_password_reused(user, password):
                    return Response({"error": "Password was used recently"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            if password:
                hashed_password = make_password(password)
                serializer.save(password=hashed_password, updated_by=request.user)
                Password_History.objects.create(user=user, password=hashed_password)
            else:
                serializer.save(updated_by=request.user)

            return Response({"success": True, "message": "User updated successfully", "data": serializer.data},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ================= DELETE USER =================
    def delete(self, request, id):
        user = get_object_or_404(User, id=id, deleted_at__isnull=True, is_active=True)
        user.deleted_at = timezone.now()
        user.is_active = False
        user.updated_by = request.user
        user.save()
        return Response({"success": True, "message": "User deleted successfully"}, status=status.HTTP_200_OK)