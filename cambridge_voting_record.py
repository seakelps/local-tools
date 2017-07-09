""" Download the cambridge city council voting records from Accela """

from html2text import html2text
import csv
import logging
from urllib.parse import parse_qsl, urlparse
from collections import defaultdict
import re
import bs4
import requests
import requests_cache
from dateutil.parser import parse as parse_dt

requests_cache.install_cache("member_history")
HISTORY = 'http://cambridgema.iqm2.com/Citizens/Detail_BoardMember.aspx?ID={member_id}&ShowAllItems=True&DateFilter=a&Action=GetVoteHistory&Page={page}'  # noqa
ITEM_LINK = 'http://cambridgema.iqm2.com/Citizens/Detail_LegiFile.aspx?MeetingID={meeting_id}&ID={item_id}'  # noqa


# from links on http://cambridgema.iqm2.com/Citizens/Board/1000-City-Council
COUNCIL = {
    1014: "Dennis J Carlone",
    1015: "Nadeem A Mazen",
    1016: "E Denise Simmons",
    1018: "Timothy J Toomey",
    1019: "Craig A Kelley",
    1020: "Leland Cheung",
    1021: "Marc C McGovern",
    1022: "David P Maher",
    1057: "Jan Devereux",
}


ITEMS = {}  # (meeting_id, item_id): (title, body, date)


def download_history(member_id):
    candidate_votes = {}

    for page in range(1, 100):  # seems to run out of info after 10 pages
        page = requests.get(HISTORY.format(member_id=member_id, page=page))
        page.raise_for_status()  # not actually 404 at end of pagination

        page_soup = bs4.BeautifulSoup(page.content, 'lxml')
        items = page_soup.find_all(id=re.compile("rptVoteHistory_lnkTitle_.*"))
        votes = page_soup.find_all(id=re.compile("rptVoteHistory_lblVote_.*"))

        assert items
        assert len(items) == len(votes)

        added = 0

        for item, vote in zip(items, votes):
            # internal ids repeated on each page
            item_element_id = int(item.attrs['id'].rsplit('_', 1)[-1])
            vote_element_id = int(vote.attrs['id'].rsplit('_', 1)[-1])
            assert vote_element_id == item_element_id  # make sure the zip will work for sanity

            qdict = dict(parse_qsl(urlparse(item.attrs['href']).query))
            try:
                key = int(qdict['MeetingID']), int(qdict['ID'])
            except KeyError:
                continue

            ITEMS[key] = item.text

            if key not in candidate_votes:
                added += 1
                candidate_votes[key] = vote.text

        if not added:
            return candidate_votes
    raise ValueError("more than 100 pages history?")


def download_descriptions():
    # updates the ITEMS dictionary

    for meeting_id, item_id in ITEMS.keys():
        url = ITEM_LINK.format(meeting_id=meeting_id, item_id=item_id)
        resp = requests.get(url)
        resp.raise_for_status()

        item_soup = bs4.BeautifulSoup(resp.content, 'lxml')
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
            import ipdb
            ipdb.set_trace()

        ITEMS[(meeting_id, item_id)] = (
            item_soup.find(id="ContentPlaceholder1_lblLegiFileTitle").text,
            body,
            date,
        )


if __name__ == "__main__":
    council_votes = defaultdict(dict)

    for member_id, councilor in COUNCIL.items():
        logging.info("processing %s", councilor)
        for item, vote in download_history(member_id).items():
            council_votes[item][councilor] = vote

    download_descriptions()

    print("saving to voting_record.csv")
    with open('voting_record.csv', 'w') as fp:
        fieldnames = ['meeting_id', 'item_id', 'date', 'item_description', 'item_body'] \
            + list(COUNCIL.values())
        record = csv.DictWriter(fp, fieldnames=fieldnames)
        record.writeheader()
        for (meeting_id, item_id), councilor_votes in council_votes.items():
            item_description, item_body, date = ITEMS[(meeting_id, item_id)]
            row = {
                "meeting_id": meeting_id,
                "item_id": item_id,
                "date": date,
                "item_description": item_description,
                "item_body": item_body,
            }
            row.update(councilor_votes)
            record.writerow(row)

    print(ITEMS[item])

    print("sample lookup")
    print(council_votes[(1557, 2145)])
