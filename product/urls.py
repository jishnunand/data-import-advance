from django.urls import path, re_path
from product import views

urlpatterns = [
    path('', views.product_list_view, name='product-list'),
    path('data/list/', views.ProductListJson.as_view(), name='product-list-data-json'),
    path('data/flush', views.data_flush, name='product-data-flush'),
    path('data/create', views.product_creation_edit, name='product-data-create'),
    path('data/<int:product_id>/edit', views.product_creation_edit, name='product-data-edit'),
    path('data/bulk-import', views.upload_file, name='product-bulk-import'),
    path('data/<int:product_id>/delete', views.product_data_delete, name='product-data-delete'),
]
