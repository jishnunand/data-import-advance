from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    class Meta:
        db_table = "product"
