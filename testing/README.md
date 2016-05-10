# Testing

Run the following scripts while checking the `.log` file and the shell to make sure nothing goes wrong.

1. `python3 dropdb` (answer with a `y` to the boolean prompt)
2. `python3 initdb`
3. `python3 manage.py addcity -f jcdecaux -c Toulouse -a Toulouse -o "Toulouse, FR" -p France -e 1`
4. `python3 scripts/import-dump.py Toulouse`
5. `python3 collect-bikes.py`
6. `python3 collect-weather.py`
7. `python3 train-regressors.py`
8. `nosetests`
