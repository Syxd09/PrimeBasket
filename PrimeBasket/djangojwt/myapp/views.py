import logging # Add logging import
from django.shortcuts import render
from rest_framework import generics, status # Import status for response codes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, ResetPasswordSerializer
from django.contrib.auth import authenticate

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            return Response({
                'refresh':str(refresh),
                'access':str(refresh.access_token),
                'user': user_serializer.data
            })
        else:
            return Response({
                'detail':'Invalid Credentials'
            }, status=401)
        
class ResetPasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ResetPasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        logger.info(f"Attempting password reset for user: {self.object.username}") # Log user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password (optional, depending on your flow)
            # if not self.object.check_password(serializer.data.get("old_password")):
            #     logger.warning(f"Password reset failed for user {self.object.username}: Incorrect old password provided.")
            #     return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            # Set the new password
            logger.info(f"Setting new password for user: {self.object.username}")
            self.object.set_password(serializer.validated_data.get("password")) # Use validated_data
            logger.info(f"Saving user object for: {self.object.username}")
            self.object.save()
            logger.info(f"Password successfully updated for user: {self.object.username}")
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK, # Use status constant
                'message': 'Password updated successfully',
                'data': []
            }
            return Response(response, status=status.HTTP_200_OK) # Add status to response

        logger.error(f"Password reset failed for user {self.object.username}: Invalid data provided. Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # Use status constant

class DashboardView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response({
            'message':'Welcome to Dashboard',
            'user': user_serializer.data
        }, 200)