from import_export import resources
from import_export.fields import Field
from .models import SellProduct


class SellProductResource(resources.ModelResource):
    product = Field(attribute='product_name', column_name='product')
    quantity = Field(attribute='quantity', column_name='quantity')
    price = Field(attribute='sell_price', column_name='price')
    total = Field(attribute='get_total_amount', column_name='total')
    paid = Field(attribute='paid_amount', column_name='paid')
    due = Field(attribute='get_due_amount', column_name='due')
    customer = Field(attribute='customer_name', column_name='customer')
    phone = Field(attribute='customer_phone', column_name='customer')
    description = Field(attribute='description', column_name='description')
    date = Field(attribute='date_added', column_name='date')

    class Meta:
        model = SellProduct
        fields = [
            'product',
            'quantity',
            'price',
            'total',
            'paid',
            'due',
            'customer',
            'customer',
            'description',
            'date',
        ]
