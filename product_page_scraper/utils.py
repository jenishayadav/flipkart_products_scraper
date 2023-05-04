#utils.py

from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

key2css_selector = {
    "title": "span.B_NuCI",
    "brand": "span.G6XhRU",
    "description": "div._1mXcCf.RmoJUa",
    "price": "div._30jeq3._16Jk6d",
    "mrp": "div._3I9_wc._2p6lqe",
    "selected_size": "a._1fGeJ5.PP89tw._2UVyXR._31hAvz",
    "all_sizes": "ul._1q8vHb > li._3V2wfe._31hAvz > a._1fGeJ5._2UVyXR._31hAvz",
    "category": "div._3GIHBu._2whKao", 
    "image_urls": "img.q6DClP",
    "rating": "div._3LWZlK",
}

allowed_multiple = {"all_sizes", "image_urls"}


def get_page(url):
    res = requests.get(url)
    res.raise_for_status()
    return res.text


def clean_url(url):
    url = urlparse(url)
    url = url._replace(query="")
    url = urlunparse(url)
    return url


def clean_data(data):
    for k, v in data.items():
        if v is None:
            continue
        if k in {"title", "brand", "description", "category", "selected_size"}:
            data[k] = v.replace("\xa0", "")
        elif k in {"price", "mrp", "rating"}:
            data[k] = float(v.replace("₹", "").replace(",", ""))
        elif k == "all_sizes":
            data[k] = [x.replace("\xa0", "") for x in v]
    return data


def scrape_from_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    container = soup.find("div", attrs={"id": "container"})
    data = {}
    for key, selector in key2css_selector.items():
        if selector is None:
            value = None
        elif key in allowed_multiple:
            value = []
            for element in container.select(
                selector
            ):  
                if element is None:
                    value.append(None)
                elif key == "image_urls":
                    value.append(element["src"])
                else:
                    value.append(element.get_text().strip())
        else:
            element = container.select_one(
                selector
            ) 
            if element is None:
                value = None
            else:
                value = element.get_text().strip()
        data[key] = value
    return clean_data(data)