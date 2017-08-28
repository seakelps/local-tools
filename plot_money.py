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
    return [
        ['Craig Kelley', 1825.99, 1098.91, 1504.76, 2231.84],
        # ['Dan Lenke', None, None, None, 0],
        # ['Hari Pillai', None, None, None, 0],
        ['Alanna Mallon', 20117.36, 39048.00, 19030.64, 100.00],
        # ['Jan Devereux', 27256.99, None, None, 8715.10],
        ['Bryan Sutton', 177.85, 300.00, 122.15, 0],
        ['Sam Gebru', 1763.83, 32383.50, 30619.67, 0.00],
        ['Gwendolyn Volmar', 4476.37, 7652.25, 3175.88, 0],
        ['Adriane Musgrave', 3554.69, 10478.14, 6923.45, 0],
        ['Dennis Carlone', 26880.02, 17310.71, 8258.56, 17827.87],
        ['Jeffrey Santos', 579.22, 3395.00, 2815.78, 0],
        ["Olivia D'Ambrosio", 1947.04, 5250.31, 3426.02, 122.75],
        ['Ronald Benjamin', 7.56, 680.92, 682.36, 9.00],
        ['Quinton Zondervan', 1180.47, 24795.88, 27125.41, 3510.00],
        ['Sean Tierney', 11332.40, 19025.29, 7692.89, 0],
        ['Paul Toner', 15739.82, 36314.25, 20574.43, 0],
        ['Nadya Okamoto', 4926.43, 7133.78, 2207.35, 0],
        ['Sumbul Siddiqui', 18281.17, 30634.60, 12353.43, 0],
        ['Vatsady Sivongxay', 9096.13, 25389.72, 16293.59, 0.00],
        ['Marc McGovern', 21488.60, 32067.05, 25545.11, 14966.66],
        ['Richard Harding', 1162.17, 0.00, 798.89, 0],
        ['Denise Simmons', 18911.16, 21403.10, 12671.73, 10179.79],
        ['Josh Burgin', 500.00, 500.00, 0.00, 0],
        # ['Gregg Moree', 0.00, None, None, 0],
        ['Timothy Toomey', 35917.95, 41022.33, 9174.05, 4069.67],
        ['Ilan Levy', 1000.00, 1000.38, 0.38, 0]
    ]


    old = [  # noqa
        # ['Jan Deveruex', 20242.08, None, None, 8715.1],  # none yet?

        # BOTTOM LEFT
        ['Bryan Sutton', 100.0, 100.0, 0.0, 0.0],

        # RIGHT
        ['Craig Kelley', 2158.88, 461.04, 534.0, 2231.84],

        # LEFT
        ['Jeffrey Santos', 215.28, 260.0, 44.72, 0.0],

        # TOP LEFT
        ['Josh Burgin', 500.0, 500.0, 0.0, 0.0],

        # TOP RIGHT
        ['Ronald Benjamin', 7.56, 680.92, 682.36, 9.0],

        ['Adriane Musgrave', 3391.05, 6298.64, 2907.59, 0.0],
        ['Alanna Marie Mallon', 17788.57, 29293.0, 11604.43, 100.0],
        ['Denise Simmons', 9851.15, 7592.33, 7920.97, 10179.79],
        ['Dennis Carlone', 31866.53, 14776.22, 737.56, 17827.87],
        ['Gwendolyn Volmar', 2736.13, 2763.26, 27.13, 0.0],
        ['Leland Cheung', 82049.82, 0.0, 8830.5, 90880.32],
        ['Marc McGovern', 24144.94, 21818.84, 12640.56, 14966.66],
        ['Nadya Okamoto', 3907.88, 4605.43, 697.55, 0.0],
        ["Olivia D'Ambrosio", 1947.04, 5250.31, 3426.02, 122.75],
        ['Paul Toner', 18277.0, 31969.25, 13692.25, 0.0],
        ['Quinton Zondervan', 5597.63, 19331.35, 17243.72, 3510.0],
        ['Sam Gebru', 946.54, 27398.5, 26451.96, 0.0],
        ['Sean Tierney', 8224.43, 13589.6, 5365.17, 0.0],
        ['Sumbul Siddiqui', 19402.56, 25569.6, 6167.04, 0.0],
        ['Timothy Toomey', 24126.3, 28180.89, 8124.26, 4069.67],
        ['Vatsady Sivongxay', 10852.85, 21962.16, 11109.31, 0.0],
    ]


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

    plt.xlabel("Raised in 2017", fontsize=20)
    plt.ylabel("Spent in 2017", fontsize=20)
    ax.annotate("Operating Balance\nfor City Council Candidates\nCambridge, MA (8/2017)",
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
    plt.savefig("money-2017-08-20.svg")
    plt.savefig("money-2017-08-20.png")


if __name__ == "__main__":
    plot_data(get_candidates())
