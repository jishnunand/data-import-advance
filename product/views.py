from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django_datatables_view.base_datatable_view import BaseDatatableView

from product.filters import ProductFilter
from product.models import Product


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


@login_required
def data_flush(request):
    """

    :param request:
    :return:
    """
    Product.objects.all().delete()
    context = {"message": "Data flush completed successfully"}
    return JsonResponse(context)
