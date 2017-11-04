""" Dump stats to make new finance graph """

from overview.models import Candidate
from campaign_finance import models as cfm
import csv
import sys


writer = csv.writer(sys.stdout)

for c in Candidate.objects.filter(is_running=True).exclude(cpf_id=None):
    try:
        balance = cfm.RawBankReport.objects\
            .filter(cpf_id=c.cpf_id)\
            .latest("filing_date").ending_balance_display
    except cfm.RawBankReport.DoesNotExist:
        balance = None

    writer.writerow((
        c.fullname,
        balance,
        cfm.get_candidate_2017_raised(c.cpf_id),
        cfm.get_candidate_2017_spent(c.cpf_id),
        cfm.get_candidate_money_at_start_of_2017(c.cpf_id),
    ))
