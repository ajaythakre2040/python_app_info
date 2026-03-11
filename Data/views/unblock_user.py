from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import User, UnblockUser
from ..serializer.unblock import UnblockUserSerializer
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser

class UnblockUserAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UnblockUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        email_id = data.get('email_id')
        mobile_number = data.get('mobile_number')

        # ✅ Check if both fields provided
        if not email_id or not mobile_number:
            return Response(
                {"success": False, "message": "Email and mobile number are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Query using both email & mobile
        query = Q(email_id__iexact=email_id) & Q(mobile_number__iexact=mobile_number)
        user = User.objects.filter(query).first()

        if not user:
            return Response({"success": False, "message": "User not found"}, status=404)

        if user.is_active:
            return Response(
                {"success": False, "message": f"User {user.email_id} is already active."},
                status=200
            )

        # Unblock user
        user.is_active = True
        user.login_attempts = 0
        user.save()

        # Safe created_by assignment
        if hasattr(request, 'user') and request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            created_by_user = request.user
        else:
            created_by_user = None

        # Save log
        try:
            UnblockUser.objects.create(
                user=user,
                email_id=user.email_id,
                mobile_number=user.mobile_number,
                created_by=created_by_user
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"Failed to log unblock: {str(e)}"},
                status=500
            )

        return Response(
            {"success": True, "message": f"User {user.email_id} unblocked successfully."},
            status=200
        )