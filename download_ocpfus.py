""" Data export has a max export size, so we search for each candidate by
cpf_id to avoid hitting the max.

Sorry for using pandas to do this, the csv export is malformed but the xlsx
works.
"""

import argparse
from tqdm import tqdm
import csv
import pandas
from datetime import datetime
import requests
import requests_cache
import zipfile
from io import BytesIO


requests_cache.install_cache("donor_history")


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

    # preseed with current
    councelors = {
        15680,  # Carlone Committee
        50019,  # Carlone for Council Recount
        16062,  # Devereux
        13783,  # Simmons Committee
        14923,  # Cheung Committee
        15589,  # McGovern Committee
        12222,  # Toomey Committee
        15615,  # Mazen Committee
        14104,  # Kelley Committee
        13740,  # Maher Committee
    }

    registration_resp = requests.get(
        "http://ocpf2.blob.core.windows.net/downloads/data/registered-all.zip")

    zip_ref = zipfile.ZipFile(BytesIO(registration_resp.content))

    # for some reason this is a csv and the individual one is a tsv
    # columns don't all seem to line up in the .txt version but do work in the xlsx.
    registered_filers = pandas.read_excel(
        BytesIO(zip_ref.read("registered-all.xlsx")),
        sheetname=1)

    # parse_dates doesn't work in read_xlst
    registered_filers['Org_Date'] = pandas.to_datetime(registered_filers['Org_Date'])
    is_candidate = registered_filers['Category_Description'] == "Depository Candidate"
    is_recent = registered_filers['Org_Date'] > datetime(2011, 1, 1)

    candidates = registered_filers[is_candidate & is_recent]
    councelors.update(candidates.CPF_ID.values)

    return councelors


def get_donors_by_candidate(cpf_id):
    # for some reason this is a tsv and cpf_id list is a csv
    return requests.get(
        "http://www.ocpf.us/Data/GetTextOutput?SearchType=A&CityCode=0&FilerCpfId={}"
        .format(cpf_id))


def get_expenditures_by_candidate(cpf_id):
    return requests.get(
        "http://www.ocpf.us/ReportData/GetReportItems?PageSize=20000&CurrentIndex=1&SortField=&SortDirection=ASC&&SearchType=B&CityCode=0&FilerCpfId={}"  # noqa
        .format(cpf_id))


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--donors", action='store_true')
    a.add_argument("--expenditures", action='store_true')
    args = a.parse_args()

    if not (args.donors or args.expenditures):
        a.print_help()
        exit(1)

    filers = get_registered_filer_ids()
    assert len(filers) < 1000

    if args.donors:
        with open("cambridge_donors.csv", "w") as fp:
            for cpf_id in filers:
                fp.write(get_donors_by_candidate(cpf_id).content.decode('utf-8'))

    if args.expenditures:
        with open("cambridge_expenditures.csv", "w") as fp:
            out = None
            for cpf_id in tqdm(filers):
                resp = get_expenditures_by_candidate(cpf_id)
                if not resp.ok:
                    print("can't grab", cpf_id)
                    continue

                for row in resp.json():
                    if not out:
                        out = csv.DictWriter(fp, fieldnames=row.keys())
                        out.writeheader()
                    out.writerow(row)
