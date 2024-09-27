from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .serializers import *
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView
from .models import *
from .serializers import RoleMasterSerializer
from rest_framework.permissions import IsAdminUser  # or custom permission class


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'email': user.email,
            'role': user.role.role_name,
        }, status=status.HTTP_200_OK)


class RoleMasterListView(generics.ListCreateAPIView):
    queryset = RoleMaster.objects.all()
    serializer_class = RoleMasterSerializer
    permission_classes = [IsAdminUser]  # Only admins can create roles

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RoleMasterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoleMaster.objects.all()
    serializer_class = RoleMasterSerializer
    permission_classes = [IsAdminUser]  # Only admins can modify roles



# User = get_user_model()

# class UserListView(ListAPIView):
#     # permission_classes = [AllowAny]
#     queryset = User.objects.all()
#     serializer_class = UserListSerializer
#     permission_classes = [IsAuthenticated]  # You can restrict access to authenticated users only, or remove this if you want public access.


User = get_user_model()

class UserDetailView(RetrieveAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def get_object(self):
        # Return the currently authenticated user
        return self.request.user