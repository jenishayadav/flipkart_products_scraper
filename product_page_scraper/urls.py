from product_page_scraper import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('url_to_data/',views.url2product),
    path('/',views.url2product),
]
