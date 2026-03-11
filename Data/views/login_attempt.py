from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from ..models import User
from ..serializer.login_attempt import UnblockUserSerializer
from django.db.models import Q

class UnblockUserAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = UnblockUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        query = Q(name__iexact=data['name'])  # name required field है

        if 'email_id' in data and data['email_id']:
            query &= Q(email_id__iexact=data['email_id'])
        if 'mobile_number' in data and data['mobile_number']:
            query &= Q(mobile_number=data['mobile_number'])

        # User filter
        user = User.objects.filter(query).first()
        if not user:
            return Response(
                {"success": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # User unblock करना
        user.is_active = True
        user.login_attempts = 0
        user.save()

        return Response(
            {"success": True, "message": f"User {user.name} unblocked successfully."},
            status=status.HTTP_200_OK
        )