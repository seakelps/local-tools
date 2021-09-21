""" Grab finance graph data from production database """

from overview.models import Candidate
from campaign_finance.models import (
    RawBankReport, get_candidate_2021_raised,
    get_candidate_2021_spent, get_candidate_money_at_start_of_2021)


candidate_data = []
for cand in Candidate.objects.exclude(is_running=False):
    try:
        latest_bank_report = RawBankReport.objects\
            .filter(cpf_id=cand.cpf_id)\
            .latest("filing_date")
    except RawBankReport.DoesNotExist:
        latest_bank_report = None

    candidate_data.append([
        cand.fullname,
        latest_bank_report.ending_balance_display if latest_bank_report else None,
        get_candidate_2021_raised(cand.cpf_id),
        get_candidate_2021_spent(cand.cpf_id),
        get_candidate_money_at_start_of_2021(cand.cpf_id)])

print(candidate_data)
