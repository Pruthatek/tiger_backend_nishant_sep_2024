# serializers.py

from rest_framework import serializers
from django.core.exceptions import ValidationError
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import OTP, User, random, RoleMaster, CityMaster, StateMaster, StoreMaster
from django.utils import timezone
from datetime import timedelta


# User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    # confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'mobile_no', 'gender', 'role']
        # extra_kwargs = {
        #     'password': {'write_only': True}
        # }

    def validate(self, attrs):
        # if attrs['password'] != attrs['confirm_password']:
        #     raise ValidationError({"password": "Passwords do not match."})
        
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
        except ValidationError:
            raise ValidationError({"email": "Invalid email address."})

        return attrs

    def create(self, validated_data):
        # Remove 'confirm_password' from validated_data before creating the user
        # validated_data.pop('confirm_password')

        # Auto-generate a unique username if it's not used
        if 'username' not in validated_data:
            validated_data['username'] = validated_data['email'].split('@')[0] + str(random.randint(1, 10000))

        # Create the user without the confirm_password field
        user = User(**validated_data)
        # user.set_password(validated_data['password'])
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


class CityMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityMaster
        fields = ['id', 'state', 'city_name']

class StateMasterSerializer(serializers.ModelSerializer):
    cities = CityMasterSerializer(many=True, read_only=True)

    class Meta:
        model = StateMaster
        fields = ['id', 'state_name', 'cities']


class StoreSignatureGSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreMaster
        fields = [
            'business_name', 'pan_no', 'business_type', 'address_line_1', 
            'address_line_2', 'pin_code', 'city', 'state', 
            'signature_hash', 'bill_image_hash', 'store_email', 
            'store_phone', 'user'
        ]
    
    # Validate if signature image or bill image is provided
    def validate(self, data):
        required_fields = ['store_name', 'pan_no', 'business_type', 'address_line_1', 
                           'address_line_2', 'pin_code', 'city', 'state']

        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field} is required.")

        gst_selection = data.get('is_gst')
        
        if gst_selection == 'I Have GSTIN Number' and not data.get('signature_hash'):
            raise serializers.ValidationError("Signature image is required if GSTIN number is provided.")
        
        if gst_selection == 'I Want To Sell Products That Exempt GSTIN' and not data.get('bill_image_hash'):
            raise serializers.ValidationError("Bill image is required for products exempted from GSTIN.")
        
        if gst_selection == 'I Don\'t Have GSTIN Number OR I Have Applied For GSTIN' and not data.get('store_email'):
            raise serializers.ValidationError("Business email is required if GSTIN is not available.")
        
        if gst_selection == 'I Don\'t Have GSTIN Number OR I Have Applied For GSTIN' and not data.get('store_phone'):
            raise serializers.ValidationError("Business phone is required if GSTIN is not available.")

        return data
    

class StoreBankDetailsSerializer(serializers.ModelSerializer):
    def validate_bank_account_number(self, value):
        """Validate that the account number is positive and of appropriate length."""
        if len(str(value)) < 9 or len(str(value)) > 18:
            raise serializers.ValidationError("Account number must be between 9 and 18 digits.")
        return value

    def validate_bank_ifsc_code(self, value):
        """Validate that IFSC code follows the standard format."""
        if not value.isalnum() or len(value) != 11:
            raise serializers.ValidationError("IFSC code must be alphanumeric and 11 characters long.")
        return value

    def validate_bank_account_holder_name(self, value):
        """Validate that account holder name only contains letters."""
        if not value.replace(" ", "").isalpha():
            raise serializers.ValidationError("Account holder name must only contain alphabets.")
        return value


    def validate_bank_account_type(self, value):
        """Validate the account type is either 'Saving' or 'Current'."""
        valid_account_types = ['Saving', 'Current']
        if value not in valid_account_types:
            raise serializers.ValidationError(f"Account type must be one of {valid_account_types}.")
        return value
    class Meta:
        model = StoreMaster
        fields = ['bank_account_number', 'bank_account_holder_name', 'bank_ifsc_code', 'bank_account_type']


class StoreCreateSerializer(serializers.ModelSerializer):
    
    def validate_store_name(self, value):
        """Ensure the store name is not empty and has a maximum length of 100 characters."""
        if not value.strip():
            raise serializers.ValidationError("Store name cannot be empty.")
        if len(value) > 100:
            raise serializers.ValidationError("Store name cannot exceed 100 characters.")
        return value

    def validate_store_description(self, value):
        """Ensure the store description does not exceed 500 characters."""
        if len(value) > 500:
            raise serializers.ValidationError("Store description cannot exceed 500 characters.")
        return value

    def validate_business_type(self, value):
        """Ensure business type is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Business type cannot be empty.")
        return value

    class Meta:
        model = StoreMaster
        fields = ['store_name', 'bank_account_number', 'business_type', 'store_description']


class StoreCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreMaster
        fields = ['is_active']
    
