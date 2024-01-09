def get_products_url(category_code: str, page: int) -> str:
    url = "https://api.digikala.com/v1/categories/{}/search/?page={}&sort=1".format(
        category_code, page
    )
    return url


def get_categories(response):
    try:
        categories = response["data"]["widgets"][5]["data"]["categories"]
    except TypeError:
        return None

    return categories


def get_products(response):
    try:
        products = response["data"]["products"]
    except TypeError:
        return None

    return products


def parse_product(product, category_code):
    try:
        data = {
            "product_id": product["id"],
            "title_fa": product["title_fa"],
            "title_en": product["title_en"],
            "price": product["default_variant"]["price"]["selling_price"],
            "uri": product["url"]["uri"],
            "category": category_code,
        }
    except TypeError:
        return None

    return data
