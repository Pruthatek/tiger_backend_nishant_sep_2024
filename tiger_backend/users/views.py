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
from rest_framework.permissions import IsAdminUser  # or custom permission class
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
import os
import hashlib
import time


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserRegistrationViewBusiness(generics.CreateAPIView):
    serializer_class = BusinessUserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# class UserLoginView(generics.GenericAPIView):
#     serializer_class = UserLoginSerializer
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data

#         refresh = RefreshToken.for_user(user)

#         return Response({
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#             'email': user.email,
#             'role': user.role.role_name,
#         }, status=status.HTTP_200_OK)



class RequestOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']  # Assuming you save the user in the serializer
            token, created = Token.objects.get_or_create(user=user)  # Get or create a token for the user
            return Response({"message": "OTP verified. Login successful.", 
                             "token": token.key,
                             "user_id": user.id }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class UserDetailView(RetrieveAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def get_object(self):
        # Return the currently authenticated user
        return self.request.user
    

class StateListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = StateMaster.objects.all()
        serializer = StateMasterSerializer(queryset, many=True)
        return Response(serializer.data)


class CityListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Get the state_id from query parameters, e.g., /api/cities/?state_id=1
        state_id = request.query_params.get('state_id', None)
        
        if state_id:
            queryset = CityMaster.objects.filter(state_id=state_id)
        else:
            queryset = CityMaster.objects.all()
        
        serializer = CityMasterSerializer(queryset, many=True)
        return Response(serializer.data)


class StoreSignatureGSTView(APIView):
    def post(self, request):
        signature_file = request.FILES.get('signature')
        ele_bill_file = request.FILES.get('electricity_bill')
        request.data['user'] = request.user.id
        if signature_file:
            # Generate a unique file name based on the current timestamp
            
            user_id = str(request.user.id)
            original_file_name = signature_file.name
            timestamp = str(int(time.time()))
            file_extension = os.path.splitext(original_file_name)[1]

            # Create hash using user ID and timestamp for unique filenames
            hashed_name = hashlib.md5(f'{user_id}_{timestamp}'.encode()).hexdigest() + file_extension
            file_path = os.path.join('media/signatures/', hashed_name)

            # Full path where the file will be saved
            full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # Save the file in the specified folder
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
            with open(full_file_path, 'wb+') as destination:
                for chunk in signature_file.chunks():
                    destination.write(chunk)

            # Store the relative file path in the data
            request.data['signature_hash'] = file_path
        if ele_bill_file:
            unique_name = f"{request.user.id} elec_bill"
            hashed_name = hashlib.md5(unique_name.encode()).hexdigest() + file_extension
            file_path = os.path.join('media/elec_bill/', hashed_name)

            # Full path where the file will be saved
            full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # Save the file in the specified folder
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
            with open(full_file_path, 'wb+') as destination:
                for chunk in signature_file.chunks():
                    destination.write(chunk)
            request.data['bill_image_hash'] = file_path
        # Proceed with the serializer
        serializer = StoreSignatureGSTSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreBankDetailsView(APIView):
    def post(self, request, format=None):
        serializer = StoreBankDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StoreCreateView(APIView):
    def post(self, request, format=None):
        serializer = StoreCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StoreCancelView(APIView):
    
    def post(self, request, pk, format=None):
        try:
            store = StoreMaster.objects.get(pk=pk)
        except StoreMaster.DoesNotExist:
            return Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)

        store.is_active = False
        store.save()
        return Response({"message": "Registration request canceled successfully"}, status=status.HTTP_200_OK)