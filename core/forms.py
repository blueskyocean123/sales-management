from django import forms
from .models import *
from allauth.account.forms import SignupForm

offices = Office.objects.all()

class MyCustomSignupForm(SignupForm):
    office = forms.ModelChoiceField(offices)

    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        office = self.cleaned_data['office']
        user.office = office
        user.save()
        return user


class HelpcenterForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': '3'}))


class UserPermissionForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username',
                'email',
                'first_name',
                'last_name',
                'is_active',
                'is_staff',]


class SupplierCreateForm(forms.ModelForm):

    class Meta:
        model = Supplier
        fields = [
            'name',
            'phone',
            'description'
        ]
        labels = {
            'name': 'Supplier (সরবরাহকারী)',
            'phone': 'Phone (নাম্বার)',
            'description': 'Description (বর্ণনা)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Number'}),
            'description': forms.Textarea(attrs={'rows': '2'}),
        }

class PurchaseCreateForm(forms.ModelForm):

    class Meta:
        model = PurchaseProduct
        fields = [
                'supplier',
                'product_name',
                'price',
                'quantity',
                'chalan_number',
                'date_added'
            ]
        labels = {
            'supplier': 'Supplier (সরবরাহকারী)',
            'product_name': 'Product (পণ্য)',
            'price': 'Price (মূল্য)',
            'quantity': 'Quantity (পরিমাণ)',
            'chalan_number': 'Chalan (চালান)',
            'date_added': 'Date (তারিখ)'
        }
        widgets = {
            # 'supplier': forms.TextInput(attrs={'placeholder': 'Name'}),
            'product_name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'price': forms.TextInput(attrs={'placeholder': 'Taka'}),
            'date_added': forms.DateInput(attrs={'placeholder': 'Date'}),
        }    


class StockCreateForm(forms.ModelForm):

    class Meta:
        model = Stock
        fields = ['product_name',
                # 'sell_price',
                'quantity',
                ]
        widgets = {
            'product_name': forms.TextInput(attrs={'placeholder': 'Name'}),
            # 'sell_price': forms.TextInput(attrs={'placeholder': 'Taka'}),
        }
        labels = {
                'product_name': 'Product (পণ্য)',
                'quantity': 'Quantity (পরিমাণ)',
                # 'sell_price': 'Sell Price (বিক্রয় মূল্য)',
        } 


class SellProductCreateForm(forms.ModelForm):

    class Meta:
        model = SellProduct
        fields = [
                'product_name',
                'quantity',
                'sack',
                'sell_price',
                'customer_name',
                'token_number',
                'paid_amount',
                'date_added',
            ]
        labels = {
                'product_name': 'Product (পণ্য)',
                'quantity': 'Quantity (পরিমাণ)',
                'sack': 'Sack (বস্তা)',
                'sell_price': 'Sell Price (বিক্রয় মূল্য)',
                'customer_name': 'Customer Name (ক্রেতার নাম)',
                'token_number': 'Token (টোকেন)',
                'paid_amount': 'Paid Amount (পরিশোধিত টাকা)',
                'date_added': 'Date (তারিখ)',
        }
        widgets = {
            'sell_price': forms.TextInput(attrs={'placeholder': 'Taka'}),
            'paid_amount': forms.TextInput(attrs={'placeholder': 'Taka'}),
            'customer_name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'token_number': forms.NumberInput(attrs={'placeholder': 'Token'}),
            'date_added': forms.DateInput(attrs={'placeholder': 'Date'}),
        }
