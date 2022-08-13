# goad


To install
- download python 
- get .env file from mike and put it alongside requirements.txt
- navigate to the folder that contains requirements.txt 
- run `python -m venv .venv` 
- run `source .venv/bin/activate` (you will need to run this in ever terminal instance)
- run `pip install`
- run `python manage.py migrate`
- run `python manage.py createsuperuser`
- run `python manage.py runserver`

- run `python manage.py qcluster` in a seperate terminal to have clusters run