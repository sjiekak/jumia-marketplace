from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup


@dataclass
class Seller:
    name: str
    location: str
    phone: str


@dataclass
class Advert:
    title: str
    description: str
    posted: datetime
    attributes: dict

    url: str
    image_urls: list[str]

    seller: Seller


def parse(markup: str | bytes) -> Advert:
    soup = BeautifulSoup(markup, "html.parser")
    raise NotImplementedError("do your job")
