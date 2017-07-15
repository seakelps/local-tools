import pandas
import numpy

df = pandas.read_csv(
    "cambridge_donors.csv",
    dtype={"Zip": str},
    parse_dates=['Date'],
    delimiter='\t')

# horrible... includes Africa
# Data is pretty messy. see 981101
df['Zip'] = df.Zip.str.strip().str.extract("(\d{5})")

df['Contributor ID'].replace(0, numpy.nan, inplace=True)
# del df['Recipient Full Name']  # redundant with CPF ID even if this is useful, it's inconsistent

df.to_csv("cambridge_donors.pretty.csv")
