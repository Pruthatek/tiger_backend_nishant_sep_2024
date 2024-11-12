from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CategoryMasterSerializer, SubcategoryMasterSerializer
from django.db import transaction
from .models import (CategoryMaster, SubcategoryMaster, BrandMaster, LinkMaster, ShopVariantMapping,
                ProductMaster, ProductVariant, VariantAttributeMapping, AttributeMaster)
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.permissions import BasePermission, IsAuthenticated 
from rest_framework.decorators import permission_classes, api_view
from tiger_backend.permissions import IsAdminOrSeller
import traceback
import posixpath
import uuid
import json
import time
import ast

def generate_short_unique_filename(extension):
    # Shortened UUID (6 characters) + Unix timestamp for uniqueness
    unique_id = uuid.uuid4().hex[:6]  # Get the first 6 characters of UUID
    timestamp = str(int(time.time()))  # Unix timestamp as a string
    return f"{unique_id}_{timestamp}{extension}"

# Get all categories
class CategoryListView(generics.ListAPIView):
    queryset = CategoryMaster.objects.filter(is_active=True)
    serializer_class = CategoryMasterSerializer


# Get subcategories, filter by category if provided
class SubcategoryListView(generics.ListAPIView):
    serializer_class = SubcategoryMasterSerializer

    def get_queryset(self):
        category_id = self.request.query_params.get('category_id', None)
        queryset = SubcategoryMaster.objects.filter(is_active=True)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    

# views.py

@csrf_exempt
def brand_list(request):
    if request.method == 'GET':
        try:
            brands = BrandMaster.objects.filter(is_active=True)
            brand_data = []
            for brand in brands:
                brand_data.append({
                    'id': brand.id,
                    'brand_name': brand.brand_name,
                    'description': brand.description,
                    'logo': brand.logo,
                    'website': brand.website,
                    'contact_email': brand.contact_email,
                    'created_by': brand.created_by,
                    'created_date': brand.created_date,
                    'updated_by': brand.updated_by,
                    'updated_date': brand.updated_date,
                    'is_active': brand.is_active,
                })
            return JsonResponse({'status': 'success', 'data': brand_data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def brand_create(request):
    if request.method == 'POST':
        try:
            if not str(request.user.role) in ['Admin', 'Seller']:
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to access this.'}, status=403)
            # Start a transaction
            with transaction.atomic():
                data = request.POST
                logo_file = request.FILES.get('logo')  # Get the logo file from the request

                # If logo file is provided, save it to the static folder
                if logo_file:
                    extension = os.path.splitext(logo_file.name)[1]  # Get the file extension
                    short_unique_filename = generate_short_unique_filename(extension)
                    fs = FileSystemStorage(location=os.path.join(settings.STATIC_ROOT, 'brand_logos'))
                    logo_path = fs.save(short_unique_filename, logo_file)
                    logo_url = posixpath.join('static/brand_logos', logo_path)
                else:
                    logo_url = data.get('logo')  # If no file is provided, use the URL provided in the request
                
                updated_by_name = request.user.username
                if not updated_by_name:
                    return JsonResponse({'status': 'error', 'message': "Please login to your business account"}, status=400)

                # Create a new brand entry
                brand = BrandMaster.objects.create(
                    brand_name=data.get('brand_name'),
                    description=data.get('description', ''),
                    logo=str(logo_url),
                    website=data.get('website', ''),
                    contact_email=data.get('contact_email', ''),
                    created_by=updated_by_name,
                )

                # Return the response with brand details
                brand_data = {
                    'id': brand.id,
                    'brand_name': brand.brand_name,
                    'description': brand.description,
                    'logo': str(brand.logo),
                    'website': brand.website,
                    'contact_email': brand.contact_email,
                    'is_active': brand.is_active,
                }
                return JsonResponse({'status': 'success', 'data': brand_data})

        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def brand_update(request, brand_id):
    if request.method == 'POST':
        if not str(request.user.role) in ['Admin', 'Seller']:
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to access this.'}, status=403)
        try:
            brand = BrandMaster.objects.get(id=brand_id)

            data = request.POST
            logo_file = request.FILES.get('logo')  # Get the logo file from the request

            if logo_file:
                extension = os.path.splitext(logo_file.name)[1]  # Get the file extension
                short_unique_filename = generate_short_unique_filename(extension)
                fs = FileSystemStorage(location=os.path.join(settings.STATIC_ROOT, 'brand_logos'))
                logo_path = fs.save(short_unique_filename, logo_file)
                logo_url = posixpath.join('static/brand_logos', logo_path)
            else:
                logo_url = data.get('logo', brand.logo)  # Use existing logo if not updated

            updated_by_name = request.user.username
            if not updated_by_name:
                return JsonResponse({'status': 'error', 'message': "Please login to your business account"}, status=400)
            # Update the brand
            brand.brand_name = data.get('brand_name', brand.brand_name)
            brand.description = data.get('description', brand.description)
            brand.logo = logo_url
            brand.website = data.get('website', brand.website)
            brand.contact_email = data.get('contact_email', brand.contact_email)
            brand.updated_by = updated_by_name
            brand.save()

            # Return the response with updated brand details
            brand_data = {
                'id': brand.id,
                'brand_name': brand.brand_name,
                'description': brand.description,
                'logo': brand.logo,
                'website': brand.website,
                'contact_email': brand.contact_email,
                'created_by': brand.created_by,
                'created_date': brand.created_date,
                'updated_by': brand.updated_by,
                'updated_date': brand.updated_date,
                'is_active': brand.is_active,
            }
            return JsonResponse({'status': 'success', 'data': brand_data})

        except BrandMaster.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Brand not found'}, status=404)
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@api_view(['DELETE'])
def brand_delete(request, brand_id):
    if request.method == 'DELETE':
        if not str(request.user.role) in ['Admin', 'Seller']:
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to access this.'}, status=403)
        try:
            brand = BrandMaster.objects.get(id=brand_id)
            brand.is_active = False
            brand.save()
            return JsonResponse({'status': 'success', 'message': 'Brand deleted successfully'})
        except BrandMaster.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Brand not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def product_register(request):
    if request.method == 'POST':
        try:
            if not str(request.user.role) in ['Admin', 'Seller']:
                return JsonResponse({'status': 'error', 'message': 'You do not have permission to access this.'}, status=403)
            # Begin a transaction
            with transaction.atomic():
                # Get data from request (you can use request.data if using DRF or request.POST for standard Django form submissions)
                data = request.POST

                # Extract necessary fields for product and variant creation
                user_name = request.user.username
                product_name = data.get('product_name')
                product_description = data.get('product_description')
                category_id = data.get('category_id')
                subcategory_id = data.get('subcategory_id')
                created_by = user_name 

                # Create the ProductMaster object
                product = ProductMaster.objects.create(
                    product_name=product_name,
                    product_description=product_description,
                    category_id=category_id,
                    subcategory_id=subcategory_id,
                    created_by=user_name,
                )

                # Create the ProductVariant
                variant_name = data.get('variant_name')
                variant_description = data.get('variant_description')
                price = data.get('price')

                variant = ProductVariant.objects.create(
                    product=product,
                    variant_name=variant_name,
                    variant_description=variant_description,
                    price=price,
                    created_by=user_name,
                )

                # Create VariantAttributeMapping entries
                attributes = data.get('attributes', {})
                if isinstance(attributes, str):  # Convert to dictionary if received as a JSON string
                    attributes = json.loads(attributes)
                for attribute_name, attribute_value in attributes.items():
                    VariantAttributeMapping.objects.create(
                        product_variant=variant,
                        attribute_name=attribute_name,
                        attribute_value=attribute_value,
                        created_by=created_by
                    )

                shop_id = data.get('shop_id')
                quantity_available = data.get('quantity_available', 0)
                discounted_price = data.get('discounted_price', None)

                if shop_id:
                    ShopVariantMapping.objects.create(
                        shop_id=shop_id,
                        variant=variant,
                        price=price,
                        discounted_price=discounted_price,
                        quantity_available=quantity_available,
                        created_by=user_name,
                    )

                # Handle images (for now storing in static folder)
                image_urls = request.FILES.getlist('image_urls')  # Use request.FILES for file uploads
                image_paths = []

                fs = FileSystemStorage(location=os.path.join(settings.STATIC_ROOT, 'product_images'))  # Define the storage location
                
                for image_file in image_urls:
                    # Generate a unique filename
                    extension = os.path.splitext(image_file.name)[1]  # Get the file extension
                    short_unique_filename = generate_short_unique_filename(extension)
                    
                    # Save the image file to the filesystem
                    saved_image = fs.save(short_unique_filename, image_file)
                    img_url = posixpath.join('static/product_images', saved_image)

                    # Add the image URL to the list of image paths
                    image_paths.append(img_url)

                    # Create a LinkMaster entry for the image
                    LinkMaster.objects.create(
                        product_variant=variant,
                        image_url=img_url,
                        is_active=True,
                    )

                # Return success response
                return JsonResponse({'status': 'success', 'message': 'Product registered successfully'})

        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)