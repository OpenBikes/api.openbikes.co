import csv
import subprocess
import sys


if __name__ == '__main__':
    with open('scripts/cities.csv', 'r') as f:
        # Skip first line
        f.readline()

        r = csv.reader(f, delimiter=';')
        for row in r:
            command = f'python manage.py addcity "{row[0]}" "{row[1]}" "{row[2]}" "{row[3]}"'
            try:
                subprocess.run(command, shell=True, check=True)
            except subprocess.CalledProcessError:
                #sys.exit()
                continue
