from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from ..models import User 
from django.conf import settings
from django.utils import timezone 
from ..models.change_reset_password import Password_Action_Log
from datetime import timedelta
from ..models.login_logout_history import Login_logout_history
from ..serializer import UserRegisterSerializer,ChangePasswordSerializer,ResetPasswordSerializer
from ..utils.password import is_password_reused,validate_custom_password
from ..utils.token_generate import token_generate
from ..models import Password_History
from django.db.models import Q
from ..permissions.authentication import LoginTokenAuthentication 
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from ..permissions.login_attempt import check_login_attempts,register_failed_attempt,reset_login_attempts
##======================================== Register API =================================#
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # generate tokens but do not record a login event – registration
        # shouldn't lock the account for later logins
        tokens = token_generate(user, request, log_history=False)

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

#================================================= Login API =========================================#

class LoginAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"success": False, "message": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # FIND USER
        # -----------------------------
        if username.isdigit():
            user = User.objects.filter(
                mobile_number=username,
                deleted_at__isnull=True
            ).first()

        elif "@" in username and "." in username:
            user = User.objects.filter(
                email_id__iexact=username,
                deleted_at__isnull=True
            ).first()

        else:
            user = User.objects.filter(
                name__iexact=username,
                deleted_at__isnull=True
            ).first()

        if not user:
            return Response(
                {"success": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # -----------------------------
        # LOGIN ATTEMPT CHECK
        # -----------------------------
        try:
            check_login_attempts(user)
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

        # -----------------------------
        # PASSWORD CHECK
        # -----------------------------
        if not check_password(password, user.password):

            register_failed_attempt(user)

            return Response(
                {"success": False, "message": "Password is incorrect"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        reset_login_attempts(user)

        # -----------------------------
        # ALREADY LOGIN CHECK (optional)
        # -----------------------------

        if not getattr(settings, "ALLOW_MULTIPLE_SESSIONS", False):
            cutoff = timezone.now() - settings.SIMPLE_JWT.get(
                "ACCESS_TOKEN_LIFETIME", timedelta(hours=10)
            )

            active_session = Login_logout_history.objects.filter(user=user,logout_time__isnull=True,login_time__gt=cutoff).first()

            if active_session:
                return Response(
                    {
                        "success": False,
                        "message": "User already logged in"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        # -----------------------------
        # GENERATE TOKENS
        # -----------------------------
        try:
            tokens = token_generate(user, request)
        except IntegrityError:
            return Response(
                {"success": False, "message": "Token generation failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "success": True,
                "message": "Login Successful",
                "data": {
                    "email_id": user.email_id,
                    "mobile_number": user.mobile_number,
                    "name": user.name,
                    "access_token": tokens["access"],
                    "refresh_token": tokens["refresh"]
                },
            },
            status=status.HTTP_200_OK,
        )
#=================================================Logout API========================================================#
class LogoutAPIView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[LoginTokenAuthentication]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"success":False,"message":"refresh_token required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)

            # mark any active session for this user as logged out
            from django.utils import timezone
            try:
                
                Login_logout_history.objects.filter(
                    user=request.user,
                    logout_time__isnull=True
                ).update(logout_time=timezone.now(), is_active=False)
            except Exception:
                pass

            token.blacklist()
            return Response({"success":True, "message":"Logout successfully"},status=status.HTTP_200_OK)
        except Exception:
            return Response({"success":False , "message":"Invalid refresh token"},status=status.HTTP_400_BAD_REQUEST)
        
#==================================Change Password API===============================================#
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [LoginTokenAuthentication]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        # Validate old password
        if not user.check_password(old_password):
            return Response(
                {"success": False, "message": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate new password format
        try:
            validate_custom_password(new_password)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent using same password as current
        if user.check_password(new_password):
            return Response(
                {"success": False, "message": "New password cannot be same as current password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check password reuse (last 3 passwords)
        if is_password_reused(user, new_password):
            return Response(
                {"success": False, "message": "New password cannot be same as last 3 passwords"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save current password to history
        Password_History.objects.create(user=user, password=user.password)

        # Update user's password
        user.set_password(new_password)
        user.save()

        # Log the password change
        Password_Action_Log.objects.create(user=user, action_by=request.user, action_type="change")

        # Keep only last 3 passwords
        old_history_ids = Password_History.objects.filter(user=user).order_by('-id')[3:].values_list('id', flat=True)
        Password_History.objects.filter(id__in=old_history_ids).delete()

        return Response({"success": True, "message": "Password changed successfully"}, status=status.HTTP_200_OK)
##==================================Reset Password ===========================================###
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
            return Response({"success":False, "message":"email_id or mobile_number is required"},status=400)
        if not new_password:
            return Response({"success":False, "message":"new password is required"},status=400)

        # ✅ Safe password validation
        try:
            validate_custom_password(new_password)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=400)

        # ✅ Get user safely
        user = User.objects.filter(Q(email_id=email_id) | Q(mobile_number=mobile_number), is_active=True).first()
        if not user:
            return Response({"success": False, "message": "User not found"}, status=404)

        # ✅ Check password reuse
        if is_password_reused(user, new_password):
            return Response({"success": False, "message": "New password cannot match last 3 passwords"}, status=400)

        # ✅ Save old password in history
        if user.password:
            Password_History.objects.create(user=user, password=user.password)

        # ✅ Set new password
        user.set_password(new_password)
        user.save()

        # ✅ Log action safely
        try:
            Password_Action_Log.objects.create(user=user, action_by=None, action_type="reset")
        except Exception as e:
            print("Password_Action_Log create failed:", e)

        # ✅ Keep only last 3 passwords
        last_ids = Password_History.objects.filter(user=user).order_by('-id')[3:].values_list('id', flat=True)
        if last_ids:
            Password_History.objects.filter(id__in=last_ids).delete()

        return Response({"success": True, "message": "Password reset successfully"}, status=200)