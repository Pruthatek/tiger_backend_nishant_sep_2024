# serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import *
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'mobile_no', 'password', 'confirm_password', 'gender', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError({"password": "Passwords do not match."})
        
         # Check if the email is already in use
        if User.objects.filter(email=attrs['email']).exists():
            raise ValidationError({"email": "Email is already in use."})

        # Check if the mobile number is already in use
        if User.objects.filter(mobile_no=attrs['mobile_no']).exists():
            raise ValidationError({"mobile_no": "Mobile number is already in use."})

        if not re.match(r'^[a-zA-Z\s]+$', attrs['name']):
            raise ValidationError({"name": "Name should not contain numbers or special characters."})
        
        # Validate mobile number (10 digits)
        if not re.match(r'^\d{10}$', attrs['mobile_no']):
            raise ValidationError({"mobile_no": "Mobile number must be 10 digits."})

        # Validate email
        try:
            validate_email(attrs['email'])
        except DjangoValidationError:
            raise ValidationError({"email": "Invalid email address."})

        return attrs

    def create(self, validated_data):
        # Remove 'confirm_password' from validated_data before creating the user
        validated_data.pop('confirm_password')

        # Auto-generate a unique username if it's not used
        if 'username' not in validated_data:
            validated_data['username'] = validated_data['email'].split('@')[0] + str(random.randint(1, 10000))

        # Create the user without the confirm_password field
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user




# class UserLoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField()

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')

#         user = User.objects.filter(email=email).first()
#         if user and user.check_password(password):
#             return user
#         raise ValidationError("Invalid credentials")


from rest_framework import serializers
from .models import OTP, User
from django.utils import timezone
from datetime import timedelta

class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        otp_instance = OTP.objects.create(user=user)
        otp_instance.send_otp()
        return otp_instance


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data['email']
        otp = data['otp']
        
        try:
            otp_record = OTP.objects.get(user__email=email, otp=otp)
            
            # Check if OTP has expired
            if otp_record.is_otp_expired():
                raise serializers.ValidationError("OTP has expired. Please request a new one.")
        
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or email.")
        
        # OTP is valid and not expired
        data['user'] = otp_record.user  # Attach the user to the validated data
        return data


class RoleMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleMaster
        fields = ['id', 'role_name', 'role_description', 'is_active']

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'mobile_no', 'gender', 'role']