import calmap
from tqdm import tqdm
from clean_donors import df
from download_ocpfus import get_registered_filer_ids

aggs = df.groupby(["Recipient CPF ID", "Date"]).Amount.agg(["sum", "count"])
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


for candidate_id in tqdm(aggs.index.levels[0]):
    name = filers[candidate_id]
    sums = aggs.loc[candidate_id, 'sum']
    counts = aggs.loc[candidate_id, 'count']

    sum_plot = plot_me(sums)
    if sum_plot:
        fig, _ = sum_plot
        fig.suptitle("$ Donated")
        fig.savefig("{}_counts.svg".format(name))

    count_plot = plot_me(counts, cmap="YlGn")
    if count_plot:
        fig, _ = count_plot
        fig.suptitle("# Donated")
        fig.savefig("{}_amounts.svg".format(name))
