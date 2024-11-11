from rest_framework import serializers
from .models import (CategoryMaster, SubcategoryMaster, 
                ProductMaster, ProductVariant, 
                BrandMaster, VariantAttributeMapping, 
                AttributeMaster, ShopVariantMapping, LinkMaster)
from django.conf import settings
import os


class CategoryMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryMaster
        fields = '__all__'

class SubcategoryMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubcategoryMaster
        fields = '__all__'


# Serializer for attributes
class VariantAttributeMappingSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.attribute_name')
    
    class Meta:
        model = VariantAttributeMapping
        fields = ['attribute_name', 'attribute_value']

    def validate(self, data):
        # Validate that the attribute exists
        if not AttributeMaster.objects.filter(attribute_name=data['attribute']['attribute_name']).exists():
            raise serializers.ValidationError(f"Attribute '{data['attribute']['attribute_name']}' does not exist.")
        return data

class ProductMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMaster
        fields = '__all__'

    def validate_product_name(self, value):
        if ProductMaster.objects.filter(product_name=value, category=self.initial_data['category'], subcategory=self.initial_data['subcategory']).exists():
            raise serializers.ValidationError("Product with this name already exists in the selected category and subcategory.")
        return value

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandMaster
        fields = '__all__'

    def validate_brand_name(self, value):
        if BrandMaster.objects.filter(brand_name=value).exists():
            raise serializers.ValidationError("Brand with this name already exists.")
        return value

    def validate_logo(self, value):
        if not value.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise serializers.ValidationError("Logo must be a valid image format (.jpg, .jpeg, .png).")
        return value

class ProductVariantSerializer(serializers.ModelSerializer):
    attributes = VariantAttributeMappingSerializer(many=True, write_only=True)
    
    class Meta:
        model = ProductVariant
        fields = ['variant_name', 'variant_description', 'price', 'link_hash', 'attributes', 'created_by']

    def create(self, validated_data):
        attributes_data = validated_data.pop('attributes')
        variant = ProductVariant.objects.create(**validated_data)
        
        # Map variant attributes
        for attr_data in attributes_data:
            attribute_instance = AttributeMaster.objects.get(attribute_name=attr_data['attribute']['attribute_name'])
            VariantAttributeMapping.objects.create(
                product_variant=variant,
                attribute=attribute_instance,
                attribute_value=attr_data['attribute_value']
            )
        return variant

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive value.")
        return value

class ShopVariantMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopVariantMapping
        fields = '__all__'

    def validate_discounted_price(self, value):
        if 'price' in self.initial_data and value > float(self.initial_data['price']):
            raise serializers.ValidationError("Discounted price cannot be greater than the original price.")
        return value


class LinkMasterSerializer(serializers.ModelSerializer):
    image_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = LinkMaster
        fields = ['image_file', 'image_url']

    def create(self, validated_data):
        image_file = validated_data.pop('image_file', None)
        if image_file:
            image_path = self.save_image_locally(image_file)
            validated_data['image_url'] = image_path

        return super().create(validated_data)

    def save_image_locally(self, image_file):
        # Save image to static folder
        folder_path = os.path.join(settings.STATIC_ROOT, "product_images")
        os.makedirs(folder_path, exist_ok=True)  # Ensure the directory exists
        image_path = os.path.join(folder_path, image_file.name)

        with open(image_path, 'wb+') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        
        # Return path in the format '/static/product_images/<filename>'
        return f"/static/product_images/{image_file.name}"
    

class ProductVariantSerializer(serializers.ModelSerializer):
    attributes = VariantAttributeMappingSerializer(many=True, write_only=True)
    images = LinkMasterSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = ProductVariant
        fields = ['variant_name', 'variant_description', 'price', 'link_hash', 'attributes', 'images', 'created_by']

    def create(self, validated_data):
        attributes_data = validated_data.pop('attributes', [])
        images_data = validated_data.pop('images', [])
        variant = ProductVariant.objects.create(**validated_data)

        # Map variant attributes
        for attr_data in attributes_data:
            attribute_instance = AttributeMaster.objects.get(attribute_name=attr_data['attribute']['attribute_name'])
            VariantAttributeMapping.objects.create(
                product_variant=variant,
                attribute=attribute_instance,
                attribute_value=attr_data['attribute_value']
            )

        # Save images
        for image_data in images_data:
            image_serializer = LinkMasterSerializer(data=image_data)
            image_serializer.is_valid(raise_exception=True)
            image_serializer.save(product_variant=variant)

        return variant