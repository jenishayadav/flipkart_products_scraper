from django.db import models


class Product(models.Model):
    url = models.URLField(verbose_name="Product URL", unique=True)
    title = models.CharField(max_length=511)
    brand = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    mrp = models.FloatField(verbose_name="MRP")
    rating = models.FloatField()
    # mobile_number = models.CharField(max_length=15, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(
        max_length=255, blank=True, null=True
    )  # TODO: Check
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# NOTE: Why are we creating a different model?
# Because a product can have multiple images. If only single image case was there,
# we could have added an ImageField in Product model itself.
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_images"
    )
    image = models.ImageField(upload_to="products/")

    def __str__(self):
        return f"Image of {self.product}"
