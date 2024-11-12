# urls.py
from django.urls import path
from .views import (
    CategoryListView,
    SubcategoryListView,
    brand_list, brand_create, brand_update, brand_delete,
    product_register
)
urlpatterns = [
    path('get_categories/', CategoryListView.as_view(), name='get_categories'),
    path('get_subcategories/', SubcategoryListView.as_view(), name='get_subcategories'),
    path('product-register/', product_register, name='product-register'), 
    path('brands/', brand_list, name='brand-list'),  # List all brands
    path('brands/create/', brand_create, name='brand-create'),  # Create a new brand
    path('brands/update/<int:brand_id>/', brand_update, name='brand-update'),  # Update an existing brand
    path('brands/delete/<int:brand_id>/', brand_delete, name='brand-delete'),

]
