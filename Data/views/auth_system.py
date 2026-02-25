from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from ..models import User 
from ..serializer import UserRegisterSerializer,ChangePasswordSerializer,ResetPasswordSerializer
from ..utils.password import is_password_reused,validate_custom_password
from ..utils.token_generate import token_generate
from ..models import Password_History
from django.db.models import Q
from ..permissions.authentication import LoginTokenAuthentication 
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
##================= Register API =================#
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = token_generate(user, request)

        return Response({
            "success": True,
            "message": "User registered successfully",
            "data": {
                "email_id": user.email_id,
                "mobile_number": user.mobile_number,
                "name": user.name,
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"]
            }
        }, status=status.HTTP_201_CREATED)

#================= Login API =================#
class LoginAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        username = (request.data.get("username")or request.data.get("mobile_number")or request.data.get("email_id"))
        password = request.data.get("password")

        if not username or not password:
            return Response(
        {"success": False, "message": "Username and password are required"},
        status=status.HTTP_400_BAD_REQUEST
    )

        # 🔹 Detect login type
        if username.isdigit():
            # Mobile number login
            user = User.objects.filter(
                mobile_number=username,
                deleted_at__isnull=True
            ).first()

        elif "@" in username:
            # Email login
            user = User.objects.filter(
                email_id__iexact=username,
                deleted_at__isnull=True
            ).first()

        else:
            # Name login
            user = User.objects.filter(
                name__iexact=username,
                deleted_at__isnull=True
            ).first()

        if not user:
            return Response(
                {"success": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔹 Password check
        if not check_password(password, user.password):
            return Response(
                {"success": False, "message": "Password is incorrect"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            tokens = token_generate(user, request)
        except IntegrityError:
            return Response(
                {"success": False, "message": "Token generation failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            "success": True,
            "message": "Login successfully",
            "data": {
                "email_id": user.email_id,
                "mobile_number": user.mobile_number,
                "name": user.name,
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"]
            }
        }, status=status.HTTP_200_OK)
#==================================Logout API=========================================#
class LogoutAPIView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[LoginTokenAuthentication]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"success":False,"message":"refresh_token required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"success":True, "message":"Logout successfully"},status=status.HTTP_200_OK)
        except Exception:
            return Response({"success":False , "message":"Invalid refresh token"},status=status.HTTP_400_BAD_REQUEST)
        
#==================================Change Password API===============================================#
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[LoginTokenAuthentication]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response({"success": False, "message":"old password is incorrect"},status=status.HTTP_400_BAD_REQUEST)
        
        if is_password_reused(user, new_password):
            return Response({"success":False,"message":"new password cannot be same as last 3 passwords"},status=status.HTTP_400_BAD_REQUEST)
        
        Password_History.objects.create(user=user, password=user.password)
        user.set_password(new_password)
        user.save()

        last_ids = Password_History.objects.filter(user=user).order_by('-id')[3:].values_list('id',flat=True)
        Password_History.objects.filter(id__in=last_ids).delete()

        return Response({"success":True, "message":"Password changed successfully"},status=status.HTTP_200_OK)
    
#==================================Reset password APi====================================#
class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email_id = serializer.validated_data.get("email_id")
        mobile_number = serializer.validated_data.get("mobile_number")
        new_password = serializer.validated_data.get("new_password")

        if not email_id and not mobile_number:
            return Response({"success":False, "message":"email_id or mobile_number is required"},status=status.HTTP_400_BAD_REQUEST)
        
        if not new_password:
            return Response({"success":False, "message":"new password is required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_custom_password(new_password)
        except serializer.ValidationError as e:
            return Response({"success": False, "message": str(e)}, status=400)

        user = User.objects.filter(Q(email_id=email_id) | Q(mobile_number=mobile_number), is_active=True).first()
        if not user:
            return Response({"success": False, "message": "User not found"}, status=404)

        if is_password_reused(user, new_password):
            return Response({"success": False, "message": "New password cannot match last 3 passwords"}, status=400)

        Password_History.objects.create(user=user, password=user.password)
        user.set_password(new_password)
        user.save()

        last_ids = Password_History.objects.filter(user=user).order_by('-id')[3:].values_list('id', flat=True)
        Password_History.objects.filter(id__in=last_ids).delete()

        return Response({"success": True, "message": "Password reset successfully"}, status=200)
