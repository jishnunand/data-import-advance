from django.shortcuts import render


def product_list_view(request):
    """

    :param request:
    :return:
    """
    context = dict()
    return render(request, 'product/index.html', context=context)
