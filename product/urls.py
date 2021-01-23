from django.urls import path, re_path
from product import views

urlpatterns = [
    path('', views.product_list_view, name='product-list'),
]