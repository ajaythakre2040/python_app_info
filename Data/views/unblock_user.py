from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import User, UnblockUser
from ..serializer.unblock import UnblockUserSerializer
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

UserModel = get_user_model()

class UnblockUserAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UnblockUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Build query
        query = Q(name__iexact=data['name'])
        if data.get('email_id'):
            query &= Q(email_id__iexact=data['email_id'])
        if data.get('mobile_number'):
            query &= Q(mobile_number=data['mobile_number'])

        user = User.objects.filter(query).first()
        if not user:
            return Response({"success": False, "message": "User not found"}, status=404)

        if user.is_active:
            return Response({"success": False, "message": f"User {user.name} is already active."}, status=200)

        # Unblock user
        user.is_active = True
        user.login_attempts = 0
        user.save()

        # ✅ Safe created_by assignment
        if getattr(request, 'user', None) and request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            created_by_user = request.user
        else:
            created_by_user = None

        # Save to UnblockUser log
        UnblockUser.objects.create(
            user=user,
            name=user.name,
            email_id=user.email_id,
            mobile_number=user.mobile_number,
            created_by=created_by_user
        )

        return Response({"success": True, "message": f"User {user.name} unblocked successfully."}, status=200)