"""
base link: cambridgema.iqm2.com/Citizens/calendar.aspx?From=1/1/2013&To=12/31/2023

want to:
get every link on that page of the form
https://cambridgema.iqm2.com/Citizens/Detail_Meeting.aspx?ID=1503
https://cambridgema.iqm2.com/Citizens/Detail_Meeting.aspx?ID=4019

then:
get all text on those links
especially text like "COM 273 #2022 : A communication was received from Cathie Zusy, regarding 2.28.22 CZ re Crowe Petition. PLACED ON FILE [Unanimous]"
which is _also_ a link

just getting all links that have the last names of all the candidates.....
"""

import csv
import logging
import re
from dataclasses import asdict, dataclass, field, fields
from datetime import date
from typing import cast
from urllib.parse import parse_qsl, urlparse

import bs4
import requests
import requests_cache
import tqdm
from dateutil.parser import parse as parse_dt
from tqdm.contrib.logging import logging_redirect_tqdm

requests_cache.install_cache("member_history")
log = logging.getLogger(__name__)


MeetingId = int
CommunicationId = int


def COMMUNICATION_URL(id: CommunicationId) -> str:
    return f"http://cambridgema.iqm2.com/Citizens/Detail_LegiFile.aspx?ID={id}"


def MEETING_URL(id: MeetingId) -> str:
    return f"https://cambridgema.iqm2.com/Citizens/Detail_Meeting.aspx?ID={id}"


@dataclass
class Communication:
    id: CommunicationId
    meeting_id: MeetingId
    doc_type: str  # communication, written protest
    name: str
    regarding: str
    date: date | None

    communication_url: str = field(init=False)
    meeting_url: str = field(init=False)

    def __post_init__(self, **kwargs):
        self.meeting_url = MEETING_URL(self.meeting_id)
        self.communication_url = COMMUNICATION_URL(self.id)


def get_all_meetings(session) -> list[MeetingId]:
    today = date.today()
    resp = session.get(
        f"https://cambridgema.iqm2.com/Citizens/calendar.aspx?From=6/26/2023&To={today.strftime('%m/%d/%Y')}"
    )
    resp.raise_for_status()

    soup = bs4.BeautifulSoup(resp.content, "html5lib")
    meetings = soup.find_all("a", href=re.compile("Detail_Meeting"))

    return [
        int(extract_query_param(meeting_a.attrs["href"], "ID"))
        for meeting_a in meetings
    ]


def extract_from_meeting(session, meeting_id: MeetingId) -> list[CommunicationId]:
    url = MEETING_URL(meeting_id)
    resp = session.get(url, timeout=10)
    resp.raise_for_status()

    soup = bs4.BeautifulSoup(resp.content, "html5lib")
    if not soup:
        raise ValueError("no soup for you")

    return [
        int(extract_query_param(a.attrs["href"], "ID"))
        for a in soup.find_all("a", string=re.compile("^COM "))
    ]


def download_communication(
    session, communication_id: CommunicationId, meeting_id: MeetingId | None = None
) -> Communication | None:
    url = COMMUNICATION_URL(communication_id)
    resp = session.get(url, timeout=10)
    resp.raise_for_status()

    soup = bs4.BeautifulSoup(resp.content, "html5lib")
    header = soup.find(id="ContentPlaceholder1_lblLegiFileTitle")
    if not header:
        log.warning("com %s: no header", communication_id)
        return None

    match = re.match(
        r"\s*(An |A |Two |Three )?(?P<doc_type>.*?)( was)?\s*(received|transmitted)?\s*(from|by)\s*(?P<name>.*),? (regarding|transmitting|proposing|thanking|support|supports|supported|supporting|urging|oppose|opposed|opposes|opposing|in opposition|in support|please|relating|relates|requesting|suggesting|explaining|expressing|continue|advising|encouraging|keep|turn|commented|commenting|related|relate|against|for|preserve|Regarding|acknowledging|declaring|concerning|voicing|approve|outlining|raising|in favor|endorsing|in recognition|announcing|spoke about|stating|reflecting|acknowledges|relative|on matters|on items|highlighting|to amend|re|submitting)\W? (?P<topic>.*)\s*",
        header.text,
    )
    if match:
        name = match.group("name").strip(",")
        doc_type = match.group("doc_type")
        regarding = match.group("topic")
    else:
        log.warning("com %s: can't parse header", communication_id)
        name = "UNKNOWN"
        doc_type = "UNKNOWN"
        regarding = header.text

    if date_str := soup.find("a", id="ContentPlaceholder1_lnkDate"):
        comment_date = parse_dt(date_str.text)
    else:
        log.warning("com %s: no comment date", communication_id)
        comment_date = None

    if not meeting_id:
        # passing in, but could derive
        meeting_id = int(
            extract_query_param(cast(bs4.Tag, comment_date).attrs["href"], "ID")
        )

    return Communication(
        id=communication_id,
        meeting_id=meeting_id,
        name=name,
        doc_type=doc_type,
        regarding=regarding,
        date=comment_date,
    )


def extract_query_param(url, param: str) -> str:
    """extract query param from url"""
    return dict(parse_qsl(urlparse(url).query))[param]


def main():
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }
    )

    with open("public_comment.csv", "a") as fp, logging_redirect_tqdm():
        writer = csv.DictWriter(fp, fieldnames=[f.name for f in fields(Communication)])
        # writer.writeheader()

        for meeting_id in tqdm.tqdm(
            get_all_meetings(session), desc="meetings", position=0
        ):
            for communication_id in tqdm.tqdm(
                extract_from_meeting(session, meeting_id),
                desc="communications",
                leave=False,
                position=1,
            ):
                try:
                    communication = download_communication(
                        session,
                        communication_id,
                        meeting_id=meeting_id,
                    )
                except requests.RequestException:
                    logging.warning("failed to scrape", exc_info=True)
                else:
                    if communication:
                        if communication.doc_type not in {
                            "written protest",
                            "communication",
                        }:
                            tqdm.tqdm.write(communication.doc_type)
                        writer.writerow(asdict(communication))


if __name__ == "__main__":
    main()
