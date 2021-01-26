import base64

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django_datatables_view.base_datatable_view import BaseDatatableView

from celery.decorators import task
from product.filters import ProductFilter
from product.models import Product
from product.forms import ProductForm, ProductBulkImportForm
from django.urls import reverse


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
    columns = ['edit', 'delete', 'name', 'sku', 'id']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['edit', 'delete', 'name', 'sku', 'id']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        if column == "edit":
            return_data = '<a href="{0}" class="text-underline" title="Edit" ' \
                          '>edit</a>'.format(reverse('product-data-edit',
                                                     kwargs={'product_id': row.id}))
            return return_data
        if column == "delete":
            return_data = '<a href="javascript:" data-href="{0}" class="text-underline data-delete" title="Delete" ' \
                          '>delete</a>'.format(reverse('product-data-delete',
                                                     kwargs={'product_id': row.id}))
            return return_data
        return super(ProductListJson, self).render_column(row, column)

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


# @login_required
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

import binascii
def upload_file(request):
    """

    :param request:
    :return:
    """
    context = dict()
    form = ProductBulkImportForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():

        # print(request.FILES['file_upload'].file.name)
        handle_uploaded_file.delay(request.FILES['file_upload'].file.name)
        return redirect('product-list')
    context['form'] = form
    return render(request, 'product/bulk-import.html', context=context)


@task(name="handle_uploaded_file")
def handle_uploaded_file(encoded_file):
    print("hello")
    print(type(encoded_file))
    with open(encoded_file, "r") as f:
        print(f)

