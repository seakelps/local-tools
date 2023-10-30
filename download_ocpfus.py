""" Data export has a max export size, so we search for each candidate by
cpf_id to avoid hitting the max.

Sorry for using pandas to do this, the csv export is malformed but the xlsx
works.
"""

import argparse
from tqdm import tqdm
import csv
import pandas
import requests
import requests_cache
import zipfile
from io import BytesIO
from datetime import timedelta

requests_cache.install_cache("donor_history", expire_after=timedelta(hours=1))


candidates_2023 = {
    # 2023 incumbents
    17206: 'burhan-azeem',
    13783: 'denise-simmons',
    15589: 'marc-mcgovern',
    17259: 'patricia-m.-nolan',
    16556: 'sumbul-siddiqui',
    16576: 'paul-f.-toner',
    # challengers who've run before
    17146: 'jivan-g.-sobrinho-wheeler',
    17580: 'frantz-pierre',
    14683: 'gregg-j.-moree',
    17593: 'joe-mcguirk',
    # new challengers
    18485: 'adrienne-klein',
    18454: 'ayah-al-zubi',
    17288: 'ayesha-wilson',
    18542: 'carrie-pasquarello',
    18510: 'cathie-zusy',
    18505: 'dan-totten',
    18567: 'doug-brown',
    18568: 'federico-muchnik',
    18564: 'hao-wang',
    18495: 'joan-pickett',
    18561: 'john-hanratty',
    18437: 'peter-hsu',
    18548: 'robert-winters',
    18461: 'vernon-k.-walker',
}


def get_registered_filer_ids():
    """ Get CPF_ID for downloading other csvs.

    This document seems to include all filers by organization date and includes
    some organizations with no candidate.

    Looking at all entries since 2011 to avoid grabbing irrevant candidates,
    but hard coding the below councelors that may have filed prior to 2011.

    Dennis J. Carlone, Jan Devereux, Mayor E. Denise Simmons, Leland Cheung,
    Vice Mayor Marc C. McGovern.  Timothy J. Toomey, Jr., Nadeem A. Mazen,
    Craig A. Kelley, and David P. Maher.
    """

    return candidates_2023

    # preseed with current
    councillors = {
        #15680: "carlone",  # Carlone Committee
        #50019: "carlone2",  # Carlone for Council Recount
        # 16062: "devereux",  # Devereux
        13783: "denise-simmons",  # Simmons Committee
        # 14923: "leland-cheung",  # Cheung Committee
        15589: "marc-mcgovern",  # McGovern Committee
        #12222: "timothy-toomey",  # Toomey Committee
        # 15615: "nadeem-mazen",  # Mazen Committee
        # 14104: "craig-kelley",  # Kelley Committee
        # 13740: "maher",  # Maher Committee

    }

    registration_resp = requests.get(
        "http://ocpf2.blob.core.windows.net/downloads/data/registered-all.zip")

    zip_ref = zipfile.ZipFile(BytesIO(registration_resp.content))

    # for some reason this is a csv and the individual one is a tsv
    # columns don't all seem to line up in the .txt version but do work in the xlsx.
    registered_filers = pandas.read_excel(
        BytesIO(zip_ref.read("registered-all.xlsx")),
        sheet_name=1)

    # parse_dates doesn't work in read_xlst
    registered_filers['Org_Date'] = pandas.to_datetime(registered_filers['Org_Date'])
    is_candidate = registered_filers['Category_Description'] == "Depository Candidate"
    is_council = registered_filers['Office_District'].isin(
        ['City Councilor, Cambridge', 'Municipal, Cambridge'])

    candidates = registered_filers[is_candidate & is_council]

    found_councillors = {id_: name.lower().replace(' ', '-')
                         for id_, name in candidates[['CPF_ID', 'Candidate_Full_Name']].values}
    found_councillors.update(councillors)
    return found_councillors


def get_donors_by_candidate(cpf_id):
    # for some reason this is a tsv and cpf_id list is a csv
    return requests.get(
        "http://www.ocpf.us/ReportData/GetTextOutput?SearchType=A&CityCode=0&FilerCpfId={}"
        .format(cpf_id))


# https://www.ocpf.us/ReportData/GetReportsAndSummary?pageSize=50&currentIndex=1&sortField=&sortDirection=DESC&reportFilerCpfId=17732&reportYear=-1&currentOnly=on&baseReportTypeId=1
def get_expenditures_by_candidate(cpf_id):
    # hack - we really need to define our own list
    if (cpf_id in [10772]):
        return

    size = 500
    for page in range(0, 20):
        # 2021 and earlier
        #resp = requests.get(
        #    "http://www.ocpf.us/ReportData/GetReportItems?PageSize={}&CurrentIndex={}&SortField=&SortDirection=ASC&SearchType=B&reportFilerCpfId={}"  # noqa
        #    .format(size, page * size + 1, cpf_id))

        # 2023
        # https://ocpf.us/ReportData/GetTextOutput?1=1&filerCpfId=16576&searchTypeCategory=B
        # GetSearchRecordTypes?searchTypeCategory=B

        # https://ocpf.us/ReportData/GetTextOutput?1=1?pageSize=50&currentIndex=1&sortField=&sortDirection=DESC&filerCpfId=16576&searchTypeCategory=B

        # https://ocpf.us/ReportData/GetItemsAndSummary?pageSize=50&currentIndex=1&sortField=&sortDirection=DESC&filerCpfId=16576&searchTypeCategory=B&withSummary=true

        url = f"http://www.ocpf.us/ReportData/GetItemsAndSummary?pageSize={size}&currentIndex={page * size + 1}&sortField=&sortDirection=DESC&filerCpfId={cpf_id}&searchTypeCategory=B"
        resp = requests.get(url)

        resp.raise_for_status()
        js = resp.json()

        if not js or "items" not in js:
            continue

        items = js["items"]

        for row in items:
            yield row


# Returns the data from the candidate > "Reports" > "Report Type: Bank Reports".
# Technically all this data is elsewhere (this data is a summary of the receipts/expenditures)
# but pre-calculated summaries are nice.
def get_bank_reports_by_candidate(cpf_id):
    return requests.get(
        #  http://www.ocpf.us/ReportData/GetReports?PageSize=20000&CurrentIndex=1&&ReportYear=-1&BaseReportTypeId=4&CurrentOnly=on&ReportFilerCpfId={}
        # https://www.ocpf.us/ReportData/GetReportsAndSummary?pageSize=50&currentIndex=1&sortField=&sortDirection=DESC&reportFilerCpfId=17732&reportYear=-1&baseReportTypeId=2&
        # https://www.ocpf.us/ReportData/GetReportsAndSummary?pageSize=2000&currentIndex=1&reportYear=-1&currentOnly=on&baseReportTypeId=4&reportFilerCpfId=17732
        "https://www.ocpf.us/ReportData/GetReportsAndSummary?pageSize=20000&currentIndex=1&reportYear=-1&currentOnly=on&baseReportTypeId=1&reportFilerCpfId={}"  # noqa
        .format(cpf_id), timeout=5)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--donors", action='store_true')
    a.add_argument("--expenditures", action='store_true')
    a.add_argument("--bankreports", action='store_true')
    args = a.parse_args()

    filers = get_registered_filer_ids()

    if not (args.donors or args.expenditures or args.bankreports):
        a.print_help()
        exit(1)

    # TODO: COMMENT HI ALEX
    if args.donors:
        with open("cambridge_donors.csv", "w") as fp:
            for cpf_id in tqdm(filers):
                fp.write(get_donors_by_candidate(cpf_id).content.decode('utf-8'))

    # TODO: COMMENT HI ALEX
    if args.expenditures:
        with open("cambridge_expenditures.csv", "w") as fp:
            out = None
            for cpf_id in tqdm(filers):
                for row in get_expenditures_by_candidate(cpf_id):
                    if not out:
                        out = csv.DictWriter(fp, fieldnames=row.keys())
                        out.writeheader()
                    out.writerow(row)

    # graps the json response, converts it to csv, saves it
    if args.bankreports:
        with open("cambridge_bank_reports.csv", "w") as fp:
            out = None
            for cpf_id in tqdm(filers):
                #print(f"processing {cpf_id}")
                response = get_bank_reports_by_candidate(cpf_id)
                if not response.ok:
                    print("there was a not ok response from ocpf.us", cpf_id)
                    print(response.status_code)
                    print(response.content)

                    continue

                items = response.json()["items"]
                # print(f"\tfound {len(items)} items")

                for row in items:
                    if not out:
                        out = csv.DictWriter(fp, fieldnames=row.keys(), extrasaction='ignore')
                        out.writeheader()
                    out.writerow(row)
