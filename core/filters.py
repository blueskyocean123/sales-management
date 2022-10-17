import django_filters
from .models import *

class SellProductFilter(django_filters.FilterSet):
    product_name = django_filters.CharFilter(field_name='product_label', lookup_expr='icontains')
    customer_name = django_filters.CharFilter(lookup_expr='icontains', label='Customer Name')
    token_number = django_filters.CharFilter(lookup_expr='exact')
    date_added = django_filters.DateFilter(field_name='date_added', lookup_expr='exact')
    start_date = django_filters.DateFilter(field_name='date_added', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='date_added', lookup_expr='lte')

    class Meta:
        model = SellProduct
        fields = [
            'product_name',
            'customer_name',
            'token_number',
            'date_added',
            'start_date',
            'end_date'
        ]


class PurchaseProductFilter(django_filters.FilterSet):
    date_added = django_filters.DateFilter(field_name='date_added', lookup_expr='exact')
    start_date = django_filters.DateFilter(field_name='date_added', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='date_added', lookup_expr='lte')

    class Meta:
        model = PurchaseProduct
        fields = [
            'date_added',
            'start_date',
            'end_date'
        ]
