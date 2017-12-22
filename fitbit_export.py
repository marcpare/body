import os
import sys
import csv
from datetime import datetime, timedelta
import fitbit

credentials = os.environ.get("FITBIT_CREDENTIALS")

if credentials is None:
	print("Expecting FITBIT_CREDENTIALS")
	sys.exit(0)

client_id, client_secret, access_token, refresh_token = credentials.split(",")

authd_client = fitbit.Fitbit(
	client_id,
	client_secret,
	access_token=access_token, 
	refresh_token=refresh_token
)

earliest_date = datetime(year=2016, month=1, day=1)
days30 = timedelta(days=30)

current_date = earliest_date

records = []

while current_date < datetime.utcnow() + days30:
	data = authd_client.get_bodyweight(
		base_date=current_date,
		period="30d")
	current_date += days30


	for d in data['weight']:
		records.append({
			'date': d['date'],
			'fat': d.get('fat', 0),
			'weight': d['weight']
		})

with open('data/fitbit2.csv', 'w', newline='') as csvfile:
    fieldnames = ['date', 'fat', 'weight']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for record in records:
    	writer.writerow(record)
