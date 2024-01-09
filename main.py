from app import app

import click
import requests
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from app.schemas import ItemSchema
from app.models import Item
from app.utils.items import (
    get_categories,
    get_products,
    get_products_url,
    parse_product,
)


@app.cli.command("collect-items")
@click.argument("count", type=click.INT)
def collect_items(count):
    categories_url = "https://api.digikala.com/v2/"
    response = requests.get(url=categories_url).json()
    categories = get_categories(response)
    if categories is None:
        return

    for category in categories:
        category_code = category["code"]
        pages_count, remainder = divmod(count, 20)
        products = []
        for page in range(1, pages_count + 2):
            url = get_products_url(category_code, page)
            response = requests.get(url=url).json()
            paginated_products = get_products(response)
            if paginated_products is None:
                continue

            if page == pages_count + 1:
                products.extend(paginated_products[:remainder])
                break
            products.extend(paginated_products)

        for product in products:
            product_data = parse_product(product, category_code)
            if product_data is None:
                continue
            try:
                validate(product_data, ItemSchema.get_schema())
            except ValidationError:
                continue

            Item.create_new_item(product_data)
