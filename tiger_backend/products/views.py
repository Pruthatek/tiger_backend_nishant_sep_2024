from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CategoryMasterSerializer, SubcategoryMasterSerializer
from django.db import transaction
from .models import (CategoryMaster, SubcategoryMaster, BrandMaster, LinkMaster,
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
                    fs = FileSystemStorage(location=os.path.join(settings.STATIC_ROOT, 'brand_logos'))
                    logo_path = fs.save(logo_file.name, logo_file)
                    logo_url = os.path.join('static/brand_logos', logo_path)
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
                fs = FileSystemStorage(location=os.path.join(settings.STATIC_ROOT, 'brand_logos'))
                logo_path = fs.save(logo_file.name, logo_file)
                logo_url = os.path.join('static/brand_logos', logo_path)
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


@csrf_exempt
def product_register(request):
    if request.method == 'POST':
        try:
            # Begin a transaction
            with transaction.atomic():
                # Get data from request (you can use request.data if using DRF or request.POST for standard Django form submissions)
                data = request.POST

                # Extract necessary fields for product and variant creation
                product_name = data.get('product_name')
                product_description = data.get('product_description')
                category_id = data.get('category_id')
                subcategory_id = data.get('subcategory_id')
                created_by = data.get('created_by')

                # Create the ProductMaster object
                product = ProductMaster.objects.create(
                    product_name=product_name,
                    product_description=product_description,
                    category_id=category_id,
                    subcategory_id=subcategory_id,
                    created_by=created_by,
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
                    created_by=created_by,
                )

                # Create VariantAttributeMapping entries
                attributes = data.getlist('attributes')  # assuming it's passed as a list
                for attribute in attributes:
                    attribute_name, attribute_value = attribute.split(":")  # Assuming format 'name:value'
                    variant_attr_mapping = VariantAttributeMapping.objects.create(
                        product_variant=variant,
                        attribute_name=attribute_name,
                        attribute_value=attribute_value,
                        created_by=created_by,
                    )

                # Handle images (for now storing in static folder)
                image_urls = data.getlist('image_urls')  # A list of image URLs
                image_paths = []
                for image_url in image_urls:
                    # Save the image locally (just an example, you'd have to handle image fetching)
                    image_path = os.path.join(settings.STATIC_ROOT, 'product_images', os.path.basename(image_url))
                    image_paths.append(image_path)

                    # Create LinkMaster entry
                    LinkMaster.objects.create(
                        product_variant=variant,
                        image_url=image_path,  # Save the local path here
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