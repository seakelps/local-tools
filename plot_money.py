""" Plot raised vs spent with buble size as current balance.
Code is split between two access points:
    get candidates: which should be run in production
    plot_data: which can be run locally to generate a new svg that gets checked in
"""


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import matplotlib.cm as cm


def get_candidates():
    from overview.models import Candidate
    from campaign_finance.models import (
        RawBankReport,
        get_candidate_2021_raised, get_candidate_2021_spent,
        get_candidate_money_at_start_of_2021)
    print('working!')

    def balance(candidate):
        try:
            return RawBankReport.objects\
                .filter(cpf_id=candidate.cpf_id)\
                .latest("filing_date")\
                .ending_balance_display
        except RawBankReport.DoesNotExist:
            pass

    print([(c.fullname,
            balance(c),
            get_candidate_2021_raised(c.cpf_id),
            get_candidate_2021_spent(c.cpf_id),
            get_candidate_money_at_start_of_2021(c.cpf_id))
           for c in Candidate.objects.filter(is_running=True)])


def plot_data(data):
    names, balances, raiseds, spends, starts = zip(*data)

    xs = np.array(raiseds)
    ys = np.array(spends)
    areas = np.array(balances)
    labels = names
    colors = cm.Accent(np.linspace(0, 1, len(ys)))

    fig, ax = plt.subplots(figsize=(20, 10))
    ax.scatter(xs, ys, s=areas * 0.06, c=colors, marker='o')
    ax.xaxis.set_major_formatter(FormatStrFormatter('$%d'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('$%d'))

    ax.grid()

    ax.set_xlim(-2000, xs.max() + 1000)
    ax.set_ylim(-4000, ys.max() + 200)

    plt.xlabel("Raised in 2021", fontsize=20)
    plt.ylabel("Spent in 2021", fontsize=20)
    ax.annotate("Operating Balance\nfor City Council Candidates\nCambridge, MA (9/2021)",
                (0.5, 0.90), ha="center", xycoords="axes fraction", fontsize=20)
    ax.annotate("cambridgecouncilcandidates.com",
                (0.98, 0.03),
                ha="right",
                xycoords="axes fraction",
                fontsize=20)

    # Manual adjusting of graph labels to avoid overlap / make it clear which
    # labels belong to which points
    for x, y, area, label, color in zip(xs, ys, areas, labels, colors):

        label = label.split(' ')[1]
        if area < 1000:
            label += "($%d)" % area
        elif area < 5000:
            label += "($%dk)" % (area / 1000)
        else:
            ax.annotate("$%dk" % (area / 1000),
                        (x, y),
                        ha="center",
                        va="center",
                        fontweight="bold",
                        fontsize=14 * (area / 82000.0) ** 0.25)

        if 'Sutton' in label:
            # BOTTOM LEFT
            ax.annotate(label,
                        (x, y),
                        xytext=(-1000, -3000),
                        arrowprops=dict(arrowstyle="fancy", color=color))
        elif 'Kelley' in label:
            # RIGHT
            ax.annotate(label,
                        (x, y),
                        xytext=(2500, 1000),
                        arrowprops=dict(arrowstyle="fancy", color=color))

        elif 'Burgin' in label:
            # BOTTOM RIGHT
            ax.annotate(label,
                        (x, y),
                        xytext=(2000, -2000),
                        arrowprops=dict(arrowstyle="fancy", color=color))
        elif 'Santos' in label:
            # LEFT
            ax.annotate(label,
                        (x, y),
                        xytext=(2000, 4500),
                        arrowprops=dict(arrowstyle="fancy", color=color))
        elif 'Harding' in label:
            # BOTTOM RIGHT
            ax.annotate(label,
                        (x, y),
                        xytext=(-2000, 2000),
                        arrowprops=dict(arrowstyle="fancy", color=color))
        elif 'Benjamin' in label:
            # TOP RIGHT
            ax.annotate(label,
                        (x, y),
                        xytext=(-1000, 5500),
                        arrowprops=dict(arrowstyle="fancy", color=color))
        elif 'Okamoto' in label:
            # TOP RIGHT
            ax.annotate(label,
                        (x, y),
                        xytext=(7500, 0),
                        arrowprops=dict(arrowstyle="fancy", color=color))
        elif 'Volmar' in label:
            # TOP RIGHT
            ax.annotate(label,
                        (x, y),
                        xytext=(9500, 2000),
                        arrowprops=dict(arrowstyle="fancy", color=color))

        elif 'Sivongxay' in label or 'Gebru' in label:
            ax.annotate(label,
                        (x, y),
                        textcoords='offset points',
                        xytext=(-20, -(area * 0.04) ** 0.5 - 10))
        else:
            ax.annotate(label,
                        (x, y),
                        textcoords='offset points',
                        xytext=(-25, (area * 0.04) ** 0.5))

    plt.tight_layout()
    plt.savefig("money-2021-09-02.svg")
    plt.savefig("money-2021-09-02.png")
