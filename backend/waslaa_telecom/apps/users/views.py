from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from waslaa_telecom.apps.users.models import User
from waslaa_telecom.apps.users.serializers import RegisterSerializer, LoginSerializer
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from waslaa_telecom.apps.users.models import PasswordResetToken
from waslaa_telecom.apps.users.serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)

from waslaa_telecom.apps.users.permissions import IsAdmin
from waslaa_telecom.apps.users.serializers import CustomerListSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Registration successful."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'message': 'Login successful.',
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)

class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerListSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.filter(role='customer')


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            # Delete any existing unused tokens
            PasswordResetToken.objects.filter(user=user, is_used=False).delete()
            # Create new token
            token = PasswordResetToken.objects.create(user=user)
            # In production send email — for now print to console
            print(f"[PASSWORD RESET] Token for {email}: {token.token}")
        except User.DoesNotExist:
            pass  # Silent — prevent email enumeration

        return Response({'detail': 'If this email exists, a reset link has been sent.'})


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token_obj = PasswordResetToken.objects.get(
                token=serializer.validated_data['token'],
                is_used=False,
            )
        except PasswordResetToken.DoesNotExist:
            raise ValidationError({'token': 'Invalid or expired token.'})

        # Reset password
        user = token_obj.user
        user.set_password(serializer.validated_data['password'])
        user.save()

        # Mark token as used
        token_obj.is_used = True
        token_obj.save()

        return Response({'detail': 'Password reset successful.'})