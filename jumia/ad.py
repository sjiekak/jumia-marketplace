from dataclasses import dataclass
from datetime import datetime

import bs4
from unidecode import unidecode


@dataclass
class Seller:
    name: str
    location: str
    phone: str


@dataclass
class Advert:
    title: str
    description: str
    timestamp: datetime | str
    attributes: dict

    url: str
    image_urls: list[str]

    price: float | None
    currency: str
    seller: Seller


def parse(markup: str | bytes) -> Advert:
    soup = bs4.BeautifulSoup(markup, "lxml")

    article = soup.find("article", class_="singlepost")

    title = article.find("span", itemprop="name").text.strip()
    description = article.find("div", itemprop="description").text.strip()

    # side elements
    aside = article.find("aside")
    url = aside.find("meta", itemprop="url")["content"].strip()
    price = aside.find("span", itemprop="price")["content"].strip()
    currency = aside.find("span", itemprop="priceCurrency")["content"].strip()
    seller_name = aside.find("span", itemprop="name").text.strip()
    seller_location = aside.find("span", itemprop="addressLocality").text.strip()
    posted_on = aside.find("time", datetime=True)["datetime"]
    
    try:
        posted_on = datetime.strptime(posted_on, "%d.%m.%Y %H:%M")
    except ValueError:
        pass
    
    try:
        phone_number = article.find("div", class_="phone-box show").find("a").text.strip()
    except AttributeError:
        phone_number = None

    # attributes
    attributes_elt = article.find("div", class_="post-attributes").find_next(
        "div", class_="new-attr-style"
    )
    attributes_raw = {}

    for elt in attributes_elt.find_all(recursive=False):
        keyword = "".join(elt.find_all(string=True, recursive=False))
        value = elt.find_next("span").text
        attributes_raw[keyword] = value

    return Advert(
        title=title,
        description=description,
        timestamp=posted_on,
        attributes=_sanitize_attributes(attributes_raw),
        url=url,
        image_urls=[],
        price=_int_or_float_if_possible(price),
        currency=currency,
        seller=Seller(seller_name, seller_location, phone_number),
    )


def _sanitize_attributes(attributes: dict) -> dict:
    """sanitize attributes
    - keys are lower case without accents
    - values are converted to numeric if possible
    """
    sanitized: dict = {}
    for key, value in attributes.items():
        # remove accents
        key = unidecode(key.strip()).lower()
        value = _int_or_float_if_possible(value.strip())
        sanitized[key] = value

    return sanitized


def _int_or_float_if_possible(value: str) -> int | float | str:
    """convert to int or float if possible"""
    try:
        value = int(value)
    except ValueError:
        try:
            value = float(value)
        except ValueError:
            pass
    return value
