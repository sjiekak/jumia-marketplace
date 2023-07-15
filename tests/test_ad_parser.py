from datetime import datetime

import pytest

from jumia.ad import Advert
from jumia.ad import Seller
from jumia.ad import parse as SUT

_car_ad = Advert(
    title="KIA Sorento 2013 Occasion Europe",
    url="https://www.jumia.cm/kia-sorento-2013-occasion-europe--pid14919888",
    posted=datetime(2013, 7, 15, 20, 24),
    attributes={
        "brand": "Kia",
        "model": "Sorento",
        "transmission": "Manuelle",
        "fuel": "Essence",
        "year": 2013,
        "mileage": 103200,
        "price": 8500000,
        "currency": "FCFA",
    },
    seller=Seller(
        name="Aurelien",
        location="Beedi",
        phone="675526945",
    ),
    description="",
    image_urls=[],
)


@pytest.mark.parametrize(
    "filename,expected", [("tests/fixtures/car_ad_kia_pid14919888.html", _car_ad)]
)
def test_parse_ad(filename, expected):
    with open(filename, "r") as file:
        file_contents = file.read()

    parsed_ad = SUT(file_contents)

    assert parsed_ad.title == expected.title
    assert parsed_ad.url == expected.url
    assert parsed_ad.seller == expected.seller
    assert parsed_ad.attributes == expected.attributes
