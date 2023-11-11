import pytest

import jumia.import_ads as SUT


def test_last_page_number():
    with open("tests/fixtures/liste.html", "r") as file:
        file_contents = file.read()

    assert SUT.last_page_number(file_contents) == 4746


@pytest.mark.asyncio
async def test_import_few_ads():
    first_page = "https://www.jumia.cm/douala/studios-chambres-a-louer"
    ads = await SUT.import_all_links(first_page, 4)
    assert ads
