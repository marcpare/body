Export Fitbit Data
===

Updating data
===

Export data from Fitbit into `data/fitbit2.csv`:

	export FITBIT_CREDENTIALS=...
	python fitbit_export.csv

Email data from Strong Settings into `data/strong.csv`

Then,

	python plot.py

Install
===

	wget https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
	bash Miniconda3-latest-MacOSX-x86_64.sh

	conda install bokeh
	conda install pandas