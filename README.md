# local-tools

## what is this?

we're going to put non-website-running tools here, for instance:
- the council voting site data scraper
- the gross median rent over the past few decades from the us census

# How to generate money data

Overall process:

locally, download the bank reports:
```bash
python download_ocpfus.py --bankreports
```

save this file into the codebase and deploy it to production

log into heroku, and start a bash session:
```
heroku login
```
```
heroku run bash --app cambridge-council
```

load the bank reports:
```
python manage.py load_bank_reports cambridge_bank_reports.csv
```

## Downloading from ocpf.us

There are a few options (and you've probably set up python better than I have):

```
~$ python3 download_ocpfus.py --bankreports
~$ python3 download_ocpfus.py --donors
~$ python3 download_ocpfus.py --expenditures
```

## Move reports to prod server

This is useful for testing but it tends to timeout:
```
heroku run 'python manage.py load_bank_reports -' < cambridge_bank_reports.csv --app cambridge-council
```

hence we've started deploying the fite and then loading it from a dyno.
