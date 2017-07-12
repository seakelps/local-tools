import pandas

df = pandas.read_csv(
    "cambridge_expenditures.csv",
    index_col="Id",
    dtype={"Zip": str},
    parse_dates=['DateDisplay'])

del df['Date']
df['Date'] = df['DateDisplay']

# Data is pretty messy. see 981101
df['Zip'] = df.Zip.str.extract("(\d{5})")


df.groupby("Zip").Amount.agg(['sum', 'count'])
