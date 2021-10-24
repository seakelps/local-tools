""" Starting with open data source for votes, layer in the text of the agenda
items from Accela """

import json
import tqdm
from html2text import HTML2Text
import logging
import bs4
import requests
import requests_cache
import datetime


requests_cache.install_cache("member_history", expire_after=datetime.timedelta(days=10))
ITEM_LINK = "http://cambridgema.iqm2.com/Citizens/Detail_LegiFile.aspx?ID={item_id}"

html2markdown = HTML2Text()
html2markdown.body_width = None

session = requests.Session()
session.headers.update({'User-Agent': ''"Mozilla/5.0 (Android; Mobile; rv:27.0) Gecko/27.0 Firefox/27.0"})

agenda_items = session.get("https://data.cambridgema.gov/resource/3g59-fvq4.json").json()


def download_title_and_description(item_id):
    url = ITEM_LINK.format(item_id=item_id)
    resp = session.get(url)

    if not resp.from_cache:
        tqdm.tqdm.write(f"fetching without cache {item_id}")
    resp.raise_for_status()

    item_soup = bs4.BeautifulSoup(resp.content.decode("utf-8"), "lxml")
    # seems like always just 1
    try:
        body = item_soup.find(id="divBody").find(class_="LegiFileSectionContents")
    except AttributeError:
        body = None
    else:
        # p inside th / td doesn't work in a browser but confuses html2text
        for p in body.select('td > p,th > p'):
            p.replaceWith(p.getText())

        body = html2markdown.handle(body.decode())

    return item_soup.find(id="ContentPlaceholder1_lblLegiFileTitle").text, body


log = logging.getLogger()
log.setLevel(logging.WARN)
log.addHandler(logging.StreamHandler())


if __name__ == "__main__":
    for agenda_item in tqdm.tqdm(agenda_items):
        agenda_item["acelatitle"], agenda_item["aceladescription"] = \
            download_title_and_description(agenda_item["resolutionid"])

    with open('voting_record.json', 'x') as fp:
        json.dump(agenda_items, fp)
