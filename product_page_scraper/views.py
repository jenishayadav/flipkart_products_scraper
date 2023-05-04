#view.py

import os
import json
import time
import asyncio
from pprint import pprint
from functools import partial
from datetime import datetime, timedelta

import requests
from django.utils import timezone
from django.core.files import File
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.core.files.temp import NamedTemporaryFile
from django.views.decorators.http import require_http_methods


from product_page_scraper.models import Product, ProductImage
from product_page_scraper.utils import (
    get_page,
    scrape_from_html,
    clean_url,
)


# Create your views here.


def product_upsert(url, product):
    data = scrape_from_html(get_page(url))

    product.url = url
    product.title = data["title"]
    product.price = data["price"]
    product.mrp = data["mrp"]
    product.brand = data["brand"]
    product.description = data.get("description")
    product.size = data.get("selected_size")
    product.category = data.get("category")
    product.rating = data.get("rating")
    product.save()

    if product.product_images.all().count() > 0:
        product.product_images.all().delete()

    for img_url in data.get("image_urls", []):
        res = requests.get(img_url)
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(res.content)
        img_temp.flush()
        product_image = ProductImage(product=product)
        product_image.image.save(
            os.path.basename(url.split("?")[0]),
            File(img_temp),
            save=True,
        )
        product_image.save()

@require_http_methods(["GET", "POST"])
def url2product(request):
    if request.method == "POST":
        payload = json.loads(request.body)
        try:
            url = payload["url"]
        except KeyError:
            return JsonResponse(
                data={"error": "Missing key 'url' in the payload"}, status=400
            )

        url = clean_url(url)

        count = Product.objects.filter(url=url).count()
        if count > 0:
            # If already exists, asynchronously check and re-fetch if required
            product = Product.objects.get(url=url)
            response = model_to_dict(product)
            response["images"] = [
                d.image.url for d in product.product_images.all()
            ]

            if product.datetime_modified < timezone.now() - timedelta(
                days=7
            ):
                product_upsert(url, product)
        else:
            product = Product()
            product_upsert(url, product)
            response = model_to_dict(product)
            response["images"] = [
                d.image.url for d in product.product_images.all()
            ]

        return JsonResponse(data=response)
    else:
        return render(
            request, "url_to_data.html"
        )
