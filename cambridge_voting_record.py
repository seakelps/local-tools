""" Download the cambridge city council voting records from Accela """

import tqdm
from html2text import html2text
import csv
import logging
from urllib.parse import parse_qsl, urlparse
from collections import defaultdict
import re
import bs4
import requests_cache
import datetime
from dateutil.parser import parse as parse_dt


session = requests_cache.CachedSession(
    "member_history", expire_after=datetime.timedelta(days=10)
)
# iqm2 doesn't work otherwise
session.headers.update(
    {"User-Agent": "Mozilla/5.0 (Android; Mobile; rv:27.0) Gecko/27.0 Firefox/27.0"}
)

HISTORY = "http://cambridgema.iqm2.com/Citizens/Detail_BoardMember.aspx?ID={member_id}&ShowAllItems=True&DateFilter=a&Action=GetVoteHistory&Page={page}"  # noqa
ITEM_LINK = "http://cambridgema.iqm2.com/Citizens/Detail_LegiFile.aspx?MeetingID={meeting_id}&ID={item_id}"  # noqa


# from links on http://cambridgema.iqm2.com/Citizens/Board/1000-City-Council
COUNCIL = {
    1014: "Dennis J. Carlone",
    1716: "Alanna Mallon",
    1021: "Marc C. McGovern",
    1368: "Sumbul Siddiqui",
    1016: "E. Denise Simmons",
    1018: "Timothy J. Toomey",
    1574: "Quinton Zondervan",
    2953: "Patty Nolan",
    2948: "Jivan Sobrinho-Wheeler",
}


ITEMS = {}  # (meeting_id, item_id): (title, body, date)


def download_history(member_id):
    candidate_votes = {}

    for page in range(1, 100):  # seems to run out of info after 10 pages
        log.debug("scraping votes for %s: page %s", member_id, page)
        page = session.get(HISTORY.format(member_id=member_id, page=page))
        page.raise_for_status()  # not actually 404 at end of pagination

        page_soup = bs4.BeautifulSoup(page.content.decode("utf-8"), "lxml")
        items = page_soup.find_all(id=re.compile("rptVoteHistory_lnkTitle_.*"))
        votes = page_soup.find_all(id=re.compile("rptVoteHistory_lblVote_.*"))

        assert items
        assert len(items) == len(votes)

        added = 0

        for item, vote in zip(items, votes):
            # internal ids repeated on each page
            item_element_id = int(item.attrs["id"].rsplit("_", 1)[-1])
            vote_element_id = int(vote.attrs["id"].rsplit("_", 1)[-1])
            assert (
                vote_element_id == item_element_id
            )  # make sure the zip will work for sanity

            qdict = dict(parse_qsl(urlparse(item.attrs["href"]).query))
            try:
                key = int(qdict["MeetingID"]), int(qdict["ID"])
            except KeyError:
                continue

            ITEMS[key] = None

            if key not in candidate_votes:
                added += 1
                candidate_votes[key] = vote.text

        if not added:
            return candidate_votes
    raise ValueError("more than 100 pages history?")


def _parse_item(content):
    item_soup = bs4.BeautifulSoup(content, "lxml")
    # seems like always just 1
    try:
        body = item_soup.find(id="divBody").find(class_="LegiFileSectionContents")
    except AttributeError:
        body = None
    else:
        body = html2text(body.decode())

    try:
        date = parse_dt(item_soup.find(id="ContentPlaceholder1_lnkDate").text).date()
    except AttributeError:
        date = None

    return (
        item_soup.find(id="ContentPlaceholder1_lblLegiFileTitle").text,
        body,
        date,
    )


def download_descriptions():
    # updates the ITEMS dictionary

    for meeting_id, item_id in tqdm.tqdm(ITEMS.keys(), desc="Policy orders"):
        url = ITEM_LINK.format(meeting_id=meeting_id, item_id=item_id)
        resp = session.get(url)

        if not resp.from_cache:
            tqdm.tqdm.write(f"fetching without cache {meeting_id=} {item_id=}")
        resp.raise_for_status()

        try:
            ITEMS[(meeting_id, item_id)] = _parse_item(resp.content.decode("utf-8"))
        except Exception as e:
            log.exception(f"error in {url}")


log = logging.getLogger()
log.setLevel(logging.WARN)
log.addHandler(logging.StreamHandler())


if __name__ == "__main__":
    council_votes = defaultdict(dict)

    for member_id, councilor in tqdm.tqdm(COUNCIL.items(), desc="Councilor"):
        log.info("processing %s", councilor)
        for item, vote in download_history(member_id).items():
            council_votes[item][councilor] = vote

    download_descriptions()

    print("saving to voting_record.csv")
    with open("voting_record-{}.csv".format(datetime.date.today()), "w") as fp:
        fieldnames = [
            "meeting_id",
            "item_id",
            "date",
            "item_description",
            "item_body",
        ] + list(COUNCIL.values())
        record = csv.DictWriter(fp, fieldnames=fieldnames)
        record.writeheader()
        for (meeting_id, item_id), councilor_votes in council_votes.items():
            try:
                item_description, item_body, date = ITEMS[(meeting_id, item_id)]
            except (TypeError, ValueError):
                print(f"never parsed {meeting_id=} {item_id=}")
            else:
                row = {
                    "meeting_id": meeting_id,
                    "item_id": item_id,
                    "date": date,
                    "item_description": item_description,
                    "item_body": item_body,
                }
                row.update(councilor_votes)
                record.writerow(row)
