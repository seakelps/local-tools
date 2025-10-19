"""
Extract councillor and notable figures from public comment scrape.

This script should be run first to identify the biggest commentors and then add them to the
OTHER_COMMENTORS. Then re-run to save the city council comments to cambridge.vote and the OTHER_COMMENTORS
stats to the explainer.
"""
from collections import defaultdict
from csv import DictReader, DictWriter

import difflib


CANDIDATES = [
        "Alborz Bejnood",
        "Alex Bowers",
        "Anne Coburn",
        "Arjun Jaikumar",
        "Ayah Al-Zubi",
        "Ayesha Wilson",
        "Burhan Azeem",
        "Caitlin Dube",
        "Caroline Hunter",
        "Cathie Zusy",
        "Dana Bullister",
        "David J. Weinstein",
        "E. Denise Simmons",
        "Elizabeth Bisio",
        "Elizabeth Hudson",
        "Eugenia Schraa Huh",
        "Jane Hirschi",
        "Jess Goetz",
        "Jia-Jing Lee",
        "Jivan Sobrinho-Wheeler",
        "John Hanratty",
        "José Luis Rojas Villarreal",
        "LaQueen Battle",
        "Lilly Havstad",
        "Louise Venden",
        "Luisa de Paula Santos",
        "Marc McGovern",
        "Melanie Gause",
        "Ned Melanson",
        "Patty Nolan",
        "Paul Toner",
        "Peter Hsu",
        "Rachel B. Weinstein",
        "Richard Harding",
        "Robert Winters",
        "Stanislav Rivkin",
        "Sumbul Siddiqui",
        "Tim Flaherty",
        "Zion Sherin",
        ]


OTHER_COMMENTORS = [
        "Young Kim",
        "Robert La Tremouille",

        "Hasson Rashid",
        "Lee Farris",
        "Kathy Watkins",

        "Carol O'Hare",
        "Suzanne Blier",
        "Marilee Meyer",
        ]


with open("public_comment.csv", "r") as pb:
    pbc = defaultdict(list)
    for row in DictReader(pb):
        for candidate in CANDIDATES + OTHER_COMMENTORS:
            if candidate in row['name']:
                print('updating', row["name"])
                row['name'] = candidate
                break
        else:
            row['name'] = row['name'].replace("regarding", "")
        pbc[row['name']].append(row)

    print(
        dict(sorted(
            [(name, len(rows)) for name, rows in pbc.items()],
            key=lambda x: x[1],
            reverse=True
        )[:20])
    )


def lookup(name, save=False):
    closest_names = difflib.get_close_matches(name, pbc.keys())

    if not closest_names:
        last_name = name.split()[-1]
        closest_names = [n for n in pbc.keys() if last_name in n]

    with open("councillor_comments.csv", "a") as out:
        out_csv = DictWriter(out, fieldnames=("Name","Date","Title","Communication URL"))
        for cn in closest_names:
            print(name, cn, len(pbc[cn]))
            if save and input("save").startswith("y"):
                for row in pbc[cn]:
                    out_csv.writerow({
                        "Name": name,
                        "Date": row["date"],
                        "Title": row["regarding"],
                        "Communication URL": row["communication_url"],
                    })


if __name__ == "__main__":
    # for candidate in CANDIDATES:
    #     lookup(candidate, save=True)

    for candidate in OTHER_COMMENTORS:
        lookup(candidate)
