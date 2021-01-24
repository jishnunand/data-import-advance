from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django_datatables_view.base_datatable_view import BaseDatatableView

from product.filters import ProductFilter
from product.models import Product
from product.forms import ProductForm, ProductBulkImportForm


def product_list_view(request):
    """

    :param request:
    :return:
    """
    context = dict()
    return render(request, 'product/index.html', context=context)


class ProductListJson(BaseDatatableView):
    """

    """
    # The model we're going to show
    model = Product

    # define the columns that will be returned
    columns = ['name', 'sku', 'id']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['name', 'sku', 'id']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def prepare_results(self, qs):
        data = []
        for item in qs:
            dictionary = dict()
            for column in self.get_columns():
                dictionary[column] = self.render_column(item, column)
            data.append(dictionary)
        return data


@login_required
def data_flush(request):
    """

    :param request:
    :return:
    """
    Product.objects.all().delete()
    context = {"message": "Data flush completed successfully"}
    return JsonResponse(context)


def product_creation_edit(request, product_id=None):
    """

    :param request:
    :param product_id:
    :return:
    """
    context = dict()
    if product_id:
        context['product_id'] = product_id
    query = get_object_or_404(Product, pk=product_id) if product_id else None
    form = ProductForm(request.POST or None, instance=query)
    if request.POST and form.is_valid():
        form.save()
        return redirect('product-list')
    else:
        context['form'] = form
    return render(request, 'product/product-creation-edit.html', context=context)


@login_required
def product_data_delete(request, product_id):
    """

    :param request:
    :param product_id:
    :return:
    """
    context = dict()
    try:
        Product.objects.get(pk=product_id).delete()
    except Product.DoesNotExist:
        context = {"message": "Requested data not available"}
    context = {"message": "Requested data removed successfully"}
    return JsonResponse(context)


def upload_file(request):
    """

    :param request:
    :return:
    """
    context = dict()
    form = ProductBulkImportForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        print(request.FILES)
        handle_uploaded_file(request.FILES['file_upload'])
        return redirect('product-list')
    context['form'] = form
    return render(request, 'product/bulk-import.html', context=context)


def handle_uploaded_file(file):
    print(file)
