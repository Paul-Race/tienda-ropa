# store/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import (Product, Category, Brand, Order, 
                    ShippingAddress, ProductReview, Coupon)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'brand', 
                 'size', 'stock', 'image', 'is_active', 'featured']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['is_active', 'featured']:
                field.widget.attrs['class'] = 'form-control'

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['street_address', 'apartment_address', 'city', 
                 'state', 'zip_code', 'default']
        widgets = {
            'default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'default':
                field.widget.attrs['class'] = 'form-control'

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'phone', 'email', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shipping_address'].queryset = ShippingAddress.objects.filter(user=user)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'tracking_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_amount', 'discount_percentage', 
                 'minimum_amount', 'valid_from', 'valid_to', 
                 'active', 'usage_limit']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'active':
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        discount_amount = cleaned_data.get('discount_amount')
        discount_percentage = cleaned_data.get('discount_percentage')
        
        if not discount_amount and not discount_percentage:
            raise forms.ValidationError(
                'Debe especificar un monto de descuento o un porcentaje.'
            )
        
        if discount_amount and discount_percentage:
            raise forms.ValidationError(
                'No puede especificar tanto monto como porcentaje de descuento.'
            )
        
        return cleaned_data

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'value': 1, 'min': 1}
        )
    )
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

class ApplyCouponForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese código de cupón'
            }
        )
    )

class ProductSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Buscar productos...'
            }
        )
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    brand = forms.ModelChoiceField(
        required=False,
        queryset=Brand.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Precio mínimo'
            }
        )
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Precio máximo'
            }
        )
    )
    size = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas las tallas')] + Product.SIZE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    order_by = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Ordenar por...'),
            ('price_asc', 'Precio: menor a mayor'),
            ('price_desc', 'Precio: mayor a menor'),
            ('name', 'Nombre'),
            ('created_at', 'Más recientes'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )