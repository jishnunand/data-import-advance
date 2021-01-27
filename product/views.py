import base64
import codecs
import csv

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django_datatables_view.base_datatable_view import BaseDatatableView

from celery.decorators import task
from product.filters import ProductFilter
from product.models import Product
from product.forms import ProductForm, ProductBulkImportForm
from django.urls import reverse
from django.db.models import Q


def product_list_view(request):
    """

    :param request:
    :return:
    """
    context = dict()
    return render(request, 'product/index.html', context=context)


def clean_filter_dict(filter_set):
   """
   Clean the dictionary for before sending to queryset filter
   """
   return {k: v for k, v in filter_set.items() if not 'columns' in k
           and not 'order[' in k and not 'draw' in k and not
           'search[' in k and not 'length' in k}


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
    order_columns = ['name', 'sku', 'id']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    # def ordering(self, qs):
    #     """ Get parameters from the request and prepare order by clause
    #         """
    #
    #     # Number of columns that are used in sorting
    #     sorting_cols = 0
    #     sort_key = 'order[{0}][column]'.format(sorting_cols)
    #     while sort_key in self._querydict:
    #         sorting_cols += 1
    #         sort_key = 'order[{0}][column]'.format(sorting_cols)
    #
    #     order = []
    #
    #     order_columns = self.columns
    #
    #     for i in range(sorting_cols):
    #         # sorting column
    #         sort_dir = 'asc'
    #         try:
    #             sort_col = int(self._querydict.get(
    #                 'order[{0}][column]'.format(i)))
    #             # sorting order
    #             sort_dir = self._querydict.get('order[{0}][dir]'.format(i))
    #         except ValueError:
    #             sort_col = 0
    #
    #         sdir = '-' if sort_dir == 'desc' else ''
    #         sortcol = order_columns[sort_col]
    #
    #         if isinstance(sortcol, list):
    #             for sc in sortcol:
    #                 order.append('{0}{1}'.format(sdir, sc.replace('.', '__')))
    #         else:
    #             order.append('{0}{1}'.format(sdir, sortcol.replace('.', '__')))
    #     print(order)
    #     if order:
    #         return qs.order_by(*order)
    #     return qs

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

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset
        q = None
        or_query = None
        search = self.request.GET.get(u'search[value]', None)

        if search:
            model_field = ['name', 'sku', 'id']
            for each_field in model_field:
                q = Q(**{"%s__icontains" % each_field: search})
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q
            qs = qs.filter(or_query)

        return qs


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


def upload_file(request):
    """

    :param request:
    :return:
    """
    context = dict()
    form = ProductBulkImportForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():

        print(request.FILES['file_upload'].name)
        file_name = "/tmp/{0}".format(request.FILES['file_upload'].name)
        with open(file_name, 'wb+') as destination:
            for chunk in request.FILES['file_upload'].chunks():
                destination.write(chunk)
        handle_uploaded_file.delay(file_name)
        return redirect('product-list')
    context['form'] = form
    return render(request, 'product/bulk-import.html', context=context)


@task(name="handle_uploaded_file")
def handle_uploaded_file(encoded_file):
    with codecs.open(encoded_file, mode='r', encoding='utf8') as csvfile:
        data = csv.DictReader(csvfile, delimiter=",")
        upload_data = list()
        for row in data:
            if len(upload_data) == 1000:
                Product.objects.bulk_create(upload_data, ignore_conflicts=True)
                upload_data = list()
                upload_data.append(Product(**row))
            else:
                upload_data.append(Product(**row))
        if upload_data:
            Product.objects.bulk_create(upload_data, ignore_conflicts=True)
