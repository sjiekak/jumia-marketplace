from dataclasses import dataclass
from datetime import datetime

import bs4
from unidecode import unidecode


@dataclass
class Seller:
    name: str
    location: str
    phone: str | None


@dataclass
class Advert:
    title: str
    description: str
    timestamp: datetime | str
    attributes: dict

    url: str
    image_urls: list[str]

    price: int | float | str
    currency: str
    seller: Seller


def _findtag(tag: bs4.Tag, *args, **kwargs) -> bs4.Tag:
    res = tag.find(*args, **kwargs)
    assert res is not None and isinstance(res, bs4.Tag)
    return res


def parse(markup: str | bytes) -> Advert:
    # mypy: disable-error-code="union-attr"
    soup = bs4.BeautifulSoup(markup, "lxml")

    article = _findtag(soup, "article", class_="singlepost")

    title = _findtag(article, "span", itemprop="name").text.strip()
    description = _findtag(article, "div", itemprop="description").text.strip()

    # side elements
    aside = _findtag(article, "aside")
    url = "".join(_findtag(aside, "meta", itemprop="url")["content"])
    price = "".join(_findtag(aside, "span", itemprop="price")["content"])
    currency = "".join(_findtag(aside, "span", itemprop="priceCurrency")["content"])
    seller_name = _findtag(aside, "span", itemprop="name").text.strip()
    seller_location = _findtag(aside, "span", itemprop="addressLocality").text.strip()
    posted_on = "".join(_findtag(aside, "time")["datetime"])

    try:
        posted_on_timestamp: datetime | str = datetime.strptime(
            posted_on, "%d.%m.%Y %H:%M"
        )
    except ValueError:
        posted_on_timestamp = posted_on

    try:
        phone_number_location = _findtag(article, "div", class_="phone-box show")
        phone_number = _findtag(phone_number_location, "a").text.strip()
    except AttributeError:
        phone_number = None

    # attributes
    attributes_elt = _findtag(article, "div", class_="post-attributes").find_next(
        "div", class_="new-attr-style"
    )
    assert isinstance(attributes_elt, bs4.Tag)
    attributes_raw = {}

    for elt in attributes_elt.find_all(recursive=False):
        keyword = "".join(elt.find_all(string=True, recursive=False))
        value = elt.find_next("span").text
        attributes_raw[keyword] = value

    return Advert(
        title=title,
        description=description,
        timestamp=posted_on_timestamp,
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
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            pass
    return value
