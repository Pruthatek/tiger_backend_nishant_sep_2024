from django.db import models
from users.models import StoreMaster

# Create your models here.
class CategoryMaster(models.Model):
    category_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    link_hash = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name


class SubcategoryMaster(models.Model):
    category = models.ForeignKey(CategoryMaster, on_delete=models.CASCADE, related_name='subcategories', null=True, blank=True)
    subcategory_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    link_hash = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.subcategory_name
    

# ProductMaster
class ProductMaster(models.Model):
    category = models.ForeignKey(CategoryMaster, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(SubcategoryMaster, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    product_name = models.CharField(max_length=255)
    product_description = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.product_name

# ProductVariant
class ProductVariant(models.Model):
    product = models.ForeignKey(ProductMaster, on_delete=models.CASCADE, related_name='variants')
    variant_name = models.CharField(max_length=255)
    variant_description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.variant_name} - {self.product.product_name}"


class LinkMaster(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='image_links')
    image_url = models.URLField(max_length=500)
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Link for {self.product_variant.variant_name} - {self.image_url}"

# ShopVariantMapping
class ShopVariantMapping(models.Model):
    shop = models.ForeignKey(StoreMaster, on_delete=models.CASCADE, related_name='shop_variants')  # Assuming 'Shop' model exists
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='shop_mappings')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity_available = models.IntegerField(default=0)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.variant.variant_name} - Shop {self.shop.id}"


class BrandMaster(models.Model):
    brand_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    logo = models.CharField(max_length=255, unique=True)
    website = models.URLField(blank=True, null=True)  # Brand website
    contact_email = models.EmailField(blank=True, null=True)  # Contact email for brand support
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.brand_name
    

class AttributeMaster(models.Model):
    attribute_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.attribute_name


# AttributeSubcategoryMapping
class AttributeSubcategoryMapping(models.Model):
    subcategory = models.ForeignKey(SubcategoryMaster, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(AttributeMaster, on_delete=models.CASCADE, related_name='subcategory_mappings')
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.subcategory.subcategory_name} - {self.attribute.attribute_name}"


# VariantAttributeMapping
class VariantAttributeMapping(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(AttributeMaster, on_delete=models.CASCADE, related_name='variant_mappings')
    attribute_value = models.CharField(max_length=255)  # Example: 'Red', 'XL'
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product_variant.variant_name} - {self.attribute.attribute_name}: {self.attribute_value}"