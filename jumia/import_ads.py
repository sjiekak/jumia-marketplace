from collections import deque
from dataclasses import dataclass

import aiohttp
from bs4 import BeautifulSoup
from bs4 import SoupStrainer


@dataclass
class CategorizedLinks:
    ads: list[str]
    pages: list[str]


def links(markup: str | bytes):
    ads: list[str] = []
    pages: list[str] = []

    for link in BeautifulSoup(markup, parse_only=SoupStrainer("a")).find_all("a"):
        if link.has_attr("href"):
            href = link["href"]

            if link.has_attr("class") and "post-link" in link["class"]:
                ads.append(href)
            elif "page=" in href:
                pages.append(href)

    return CategorizedLinks(ads, pages)


def last_page_number(markup: str | bytes):
    value = 0

    for link in BeautifulSoup(markup, parse_only=SoupStrainer("a")).find_all("a"):
        if link.has_attr("href"):
            href = link["href"]
            if "page=" in href:
                try:
                    current_value = int(str(link.string))
                    if current_value > value:
                        value = current_value
                except ValueError:
                    pass
    return value


async def import_all_links(start_link: str, page_limit: int):
    async with aiohttp.ClientSession() as session:
        return await _import_all_links(session, start_link, page_limit)


async def _import_all_links(
    session: aiohttp.ClientSession, start_link: str, limit: int
):
    async with session.get(start_link) as response:
        contents = await response.text()
        last_page = last_page_number(contents)

    visited = set()

    ads = []

    to_visit = deque(start_link)
    while to_visit:
        next_link = to_visit.popleft()
        if next_link in visited:
            continue
        visited.add(next_link)
        if limit >= 0 and len(visited) > limit:
            break

        async with session.get(start_link) as response:
            contents = await response.text()
        try:
            cat_links = links(contents)
        except Exception as e:
            continue

        to_visit.extend(cat_links.pages)
        ads.extend(cat_links.ads)

    return ads
