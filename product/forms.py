from django import forms
from product.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class ProductBulkImportForm(forms.Form):
    file_upload = forms.FileField()
