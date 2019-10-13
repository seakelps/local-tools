import calmap
from tqdm import tqdm
from clean_donors import df as donors
from clean_expenditures import df as spend
from download_ocpfus import get_registered_filer_ids

donor_aggs = donors.groupby(["Recipient CPF ID", "Date"]).Amount.agg(["sum", "count"])
spend_aggs = spend.groupby(["CpfId", "Date"]).Amount.agg(["sum", "count"])
filers = get_registered_filer_ids()


def plot_me(ff, **kwargs):
    ff = ff[ff.index.year > 2014]

    # IndexErrors out when size 0
    if ff.size:
        return calmap.calendarplot(
            ff,
            monthticks=3,
            daylabels='MTWTFSS',
            dayticks=[0, 2, 4, 6],
            **kwargs)


for candidate_id in tqdm(donor_aggs.index.levels[0]):
    name = filers[candidate_id]
    donor_sums = donor_aggs.loc[candidate_id, 'sum']
    donor_counts = donor_aggs.loc[candidate_id, 'count']

    sum_plot = plot_me(donor_sums)
    if sum_plot:
        fig, _ = sum_plot
        fig.suptitle("$ Donated")
        fig.savefig("charts/calendars/raised/{}_amounts.svg".format(name))

    count_plot = plot_me(donor_counts, cmap="YlGn")
    if count_plot:
        fig, _ = count_plot
        fig.suptitle("# Donated")
        fig.savefig("charts/calendars/raised/{}_counts.svg".format(name))


for candidate_id in tqdm(spend_aggs.index.levels[0]):
    name = filers[candidate_id]
    spend_sums = spend_aggs.loc[candidate_id, 'sum']
    spend_counts = spend_aggs.loc[candidate_id, 'count']

    sum_plot = plot_me(spend_sums)
    if sum_plot:
        fig, _ = sum_plot
        fig.suptitle("$ Spent")
        fig.savefig("charts/calendars/spends/{}_amounts.svg".format(name))

    count_plot = plot_me(spend_counts, cmap="YlGn")
    if count_plot:
        fig, _ = count_plot
        fig.suptitle("# Spent")
        fig.savefig("charts/calendars/spends/{}_counts.svg".format(name))
