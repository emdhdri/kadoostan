from app import app
import click
from app.models import Item
import requests
from typing import Dict, Any, Optional
from app.schemas import ItemSchema
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import math

COLORS = {
    "red": "\033[1;31m",
    "green": "\033[1;32m",
    "white": "\033[1;37m",
    "yellow": "\033[1;33m",
}


def print_message(message, text_color=COLORS["white"]):
    colored_message = f"{text_color}{message}"
    print(colored_message)


def parse_product(product, category_code) -> Optional[Dict[str, Any]]:
    try:
        data = {
            "product_id": product["id"],
            "title_fa": product["title_fa"],
            "title_en": product["title_en"],
            "price": product["default_variant"]["price"]["selling_price"],
            "uri": product["url"]["uri"],
            "category": category_code,
        }
    except:
        return None

    return data


@app.cli.command("collect-data")
@click.argument("count")
def collect_data(count):
    count = int(count)
    categories_url = "https://api.digikala.com/v2/"
    print_message("Getting categories", COLORS["white"])
    response = requests.get(url=categories_url).json()
    categories = response["data"]["widgets"][5]["data"]["categories"]

    total_saved = 0
    for index, category in enumerate(categories, start=1):
        category_code = category["code"]
        print_message("{}. Getting {} products".format(index, category_code))
        raw_url = "https://api.digikala.com/v1/categories/{}/search/?page={}&sort=1"
        pages, remainder = divmod(count, 20)
        products = []
        for page in range(1, pages + 2):
            url = raw_url.format(category_code, page)
            response = requests.get(url=url).json()
            if page == pages + 1:
                products.extend(response["data"]["products"][:remainder])
                break
            products.extend(response["data"]["products"])

        for product in products:
            product_data = parse_product(product, category_code)
            product_repr = f"category {category_code} product {product['id']}"
            if product_data is None:
                print_message("{} is Invalid".format(product_repr), COLORS["red"])
                continue
            try:
                validate(product_data, ItemSchema.get_schema())
            except ValidationError:
                print_message("{} is Invalid".format(product_repr), COLORS["red"])
                continue
            item = Item.create_new_item(product_data)
            if item is None:
                print_message("{} exists!".format(product_repr), COLORS["yellow"])
            else:
                total_saved += 1
                print_message("{} saved".format(product_repr), COLORS["green"])
    print_message("Saved {} Items".format(total_saved), COLORS["green"])
