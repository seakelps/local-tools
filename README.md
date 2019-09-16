# local-tools

## what is this?

we're going to put non-website-running tools here, for instance:
- the council voting site data scraper
- the gross median rent over the past few decades from the us census

# How to generate money data

I DON'T REMEMBER AND WISH I'D WRITTEN IT DOWN.

DON'T BE LIKE ME.
WRITE IT DOWN.

## Downloading from ocpf.us

There are a few options (and you've probably set up python better than I have):

```
~$ python3 download_ocpfus.py --bankreports
~$ python3 download_ocpfus.py --donors
~$ python3 download_ocpfus.py --expenditures
```

## Move reports to prod server

```
heroku run 'python manage.py load_bank_reports -' < cambridge_bank_reports.csv --app cambridge-council
```

... maybe?
