
from datetime import datetime
import csv
import numpy as np
import pandas
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.charts import Scatter
from bokeh.models import HoverTool

dateparse = lambda x: pandas.datetime.strptime(x, '%Y-%m-%d')
strongdateparse = lambda x: pandas.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

def whitelist_columns(df, columns):
	for column in df.columns.values:
		if column not in columns:
			df.drop(column, axis=1, inplace=True)

fitbit = pandas.read_csv('data/fitbit.csv', parse_dates=['dateTime'], date_parser=dateparse)
caliper = pandas.read_csv('data/caliper.csv', parse_dates=['date'], date_parser=dateparse)
ultrasound = pandas.read_csv('data/ultrasound.csv', parse_dates=['date'], date_parser=dateparse)

whitelist_columns(fitbit, ['dateTime', 'body-weight', 'body-fat'])

# Data before this time is bad
fitbit = fitbit[fitbit['dateTime'] > datetime(2015, 12, 28)]

fitbit['body-fat'] -= 7

fitbit_rolling = pandas.rolling_mean(fitbit['body-fat'], window=7)

p = figure(title="Compare body fat measurement methods", x_axis_type='datetime')

# Use these colors:
# http://bl.ocks.org/aaizemberg/78bd3dade9593896a59d
p.circle(fitbit['dateTime'], fitbit_rolling, color='#c6dbef', legend="scale - 7")
p.circle(caliper['date'], caliper['caliper-body-fat'], color='#ff7f0e', legend="caliper")
p.circle(ultrasound['date'], ultrasound['ultrasound-body-fat'], color='#2ca02c', legend="ultrasound")

p.legend.location = 'top_right'
p.legend.background_fill_alpha = 0.25
p.grid[0].ticker.desired_num_ticks = 15

show(gridplot(p, ncols=1, nrows=5, plot_width=800, plot_height=400))
