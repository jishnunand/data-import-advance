from django.urls import path, re_path
from product import views

urlpatterns = [
    path('', views.product_list_view, name='product-list'),
    path('data/list/', views.ProductListJson.as_view(), name='product-list-data-json'),
    path('data/flush', views.data_flush, name='product-data-flush'),
]
