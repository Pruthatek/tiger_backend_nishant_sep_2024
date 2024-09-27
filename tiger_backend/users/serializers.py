# serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import *

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'mobile_no', 'password', 'confirm_password', 'gender', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        # Check if passwords match
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError({"password": "Passwords do not match."})

        # Check if the email is already in use
        if User.objects.filter(email=attrs['email']).exists():
            raise ValidationError({"email": "Email is already in use."})

        # Check if the mobile number is already in use
        if User.objects.filter(mobile_no=attrs['mobile_no']).exists():
            raise ValidationError({"mobile_no": "Mobile number is already in use."})

        return attrs

    def create(self, validated_data):
        # Remove 'confirm_password' from validated_data before creating the user
        validated_data.pop('confirm_password')

        # Use the email as the username
        validated_data['username'] = validated_data['email']

        # Create the user
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            return user
        raise ValidationError("Invalid credentials")

class RoleMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleMaster
        fields = ['id', 'role_name', 'role_description', 'is_active']

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'gender', 'role']