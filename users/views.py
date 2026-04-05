from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer
from .models import EmailVerification, PasswordReset

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Registration successful",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe"
                        }
                    }
                }
            ),
            400: "Validation error"
        },
        operation_description="Register a new user account"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Create email verification token
            verification = EmailVerification.objects.create(user=user)

            # Send verification email
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification.token}"
            html_message = render_to_string('emails/verification_email.html', {
                'user': user,
                'verification_url': verification_url
            })

            send_mail(
                subject='Verify your email - Bazar',
                message=f'Please verify your email by clicking: {verification_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            # Don't return tokens yet - user must verify email first
            user_data = UserProfileSerializer(user).data

            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'user': user_data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe"
                        }
                    }
                }
            ),
            400: "Invalid credentials",
            429: "Too many login attempts"
        },
        operation_description="Login with email and password (max 5 attempts per minute)"
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Check if email is verified
            if not user.email_verified:
                return Response({
                    'error': 'Email not verified',
                    'message': 'Please verify your email address before logging in. Check your inbox for the verification link.',
                    'email': user.email
                }, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)
            user_data = UserProfileSerializer(user).data

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token to blacklist')
            }
        ),
        responses={
            205: "Logout successful",
            400: "Invalid token"
        },
        operation_description="Logout by blacklisting the refresh token",
        security=[{'Bearer': []}]
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: UserProfileSerializer,
        },
        operation_description="Get current user profile",
        security=[{'Bearer': []}]
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: "Validation error"
        },
        operation_description="Update current user profile (partial update)",
        security=[{'Bearer': []}]
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BecomeSellerView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Successfully became a seller",
                examples={
                    "application/json": {
                        "message": "You are now a seller",
                        "is_seller": True
                    }
                }
            ),
            400: "Already a seller"
        },
        operation_description="Become a seller (any authenticated user can become a seller)",
        security=[{'Bearer': []}]
    )
    def post(self, request):
        user = request.user
        if user.is_seller:
            return Response(
                {'message': 'You are already a seller'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_seller = True
        user.save()

        return Response({
            'message': 'You are now a seller',
            'is_seller': True
        }, status=status.HTTP_200_OK)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Email verified successfully",
                examples={
                    "application/json": {
                        "message": "Email verified successfully",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "email_verified": True
                        }
                    }
                }
            ),
            400: "Invalid or expired token"
        },
        operation_description="Verify email address with token"
    )
    def post(self, request, token):
        try:
            verification = EmailVerification.objects.get(token=token)

            if verification.is_used:
                return Response({
                    'error': 'Token already used'
                }, status=status.HTTP_400_BAD_REQUEST)

            if verification.is_expired():
                return Response({
                    'error': 'Token expired',
                    'message': 'Verification link has expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Mark email as verified
            user = verification.user
            user.email_verified = True
            user.save()

            # Mark token as used
            verification.is_used = True
            verification.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            user_data = UserProfileSerializer(user).data

            return Response({
                'message': 'Email verified successfully',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_data
            }, status=status.HTTP_200_OK)

        except EmailVerification.DoesNotExist:
            return Response({
                'error': 'Invalid verification token'
            }, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address')
            }
        ),
        responses={
            200: "Verification email sent",
            400: "Email already verified or not found"
        },
        operation_description="Resend verification email"
    )
    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)

            if user.email_verified:
                return Response({
                    'error': 'Email already verified'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create new verification token
            verification = EmailVerification.objects.create(user=user)

            # Send verification email
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification.token}"
            html_message = render_to_string('emails/verification_email.html', {
                'user': user,
                'verification_url': verification_url
            })

            send_mail(
                subject='Verify your email - Bazar',
                message=f'Please verify your email by clicking: {verification_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            return Response({
                'message': 'Verification email sent successfully'
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address')
            }
        ),
        responses={
            200: "Password reset email sent",
            400: "User not found"
        },
        operation_description="Request password reset email"
    )
    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)

            # Create password reset token
            reset = PasswordReset.objects.create(user=user)

            # Send password reset email
            reset_url = f"{settings.FRONTEND_URL}/password-reset/confirm/{reset.token}"
            html_message = render_to_string('emails/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url
            })

            send_mail(
                subject='Reset your password - Bazar',
                message=f'Reset your password by clicking: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            return Response({
                'message': 'Password reset email sent successfully'
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            return Response({
                'message': 'If an account exists with this email, you will receive a password reset link.'
            }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['token', 'password'],
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Reset token'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='New password')
            }
        ),
        responses={
            200: "Password reset successful",
            400: "Invalid or expired token"
        },
        operation_description="Confirm password reset with token"
    )
    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')

        if not password or len(password) < 8:
            return Response({
                'error': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset = PasswordReset.objects.get(token=token)

            if reset.is_used:
                return Response({
                    'error': 'Token already used'
                }, status=status.HTTP_400_BAD_REQUEST)

            if reset.is_expired():
                return Response({
                    'error': 'Token expired',
                    'message': 'Reset link has expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Reset password
            user = reset.user
            user.set_password(password)
            user.save()

            # Mark token as used
            reset.is_used = True
            reset.save()

            return Response({
                'message': 'Password reset successfully. You can now login with your new password.'
            }, status=status.HTTP_200_OK)

        except PasswordReset.DoesNotExist:
            return Response({
                'error': 'Invalid reset token'
            }, status=status.HTTP_400_BAD_REQUEST)


