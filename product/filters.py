import django_filters as filters

from product.models import Product


class ProductFilter(filters.FilterSet):
    """
    Filtering the product data product model
    """
    class Meta:
        model = Product
        fields = ['name', 'sku']
