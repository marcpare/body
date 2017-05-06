# TODO: Unroll Stronglifts data, merge with Strong data
# TODO: Mark computed 1RM in all lift data
# TODO: add Back Squat to plots
# TODO: remove outlier front squat entry

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
strong = pandas.read_csv('data/strong.csv', parse_dates=['Date'], date_parser=strongdateparse)

whitelist_columns(fitbit, ['dateTime', 'body-weight', 'body-fat'])

# Data before this time is bad
fitbit = fitbit[fitbit['dateTime'] > datetime(2015, 12, 28)]

# Add dummy data to start/end of data so that axes line up
min_timestamp = (pandas.Series([fitbit['dateTime'].min(), caliper['date'].min(), strong['Date'].min()]).min())
max_timestamp = (pandas.Series([fitbit['dateTime'].max(), caliper['date'].max(), strong['Date'].max()]).max())

fitbit = fitbit.append(
	pandas.DataFrame({
		'dateTime': max_timestamp, 
		'body-weight': fitbit['body-weight'].iloc[-1], 
		'body-fat': fitbit['body-fat'].iloc[-1]
	}, index=[0]))

fitbit = fitbit.append(
	pandas.DataFrame({
		'dateTime': min_timestamp, 
		'body-weight': fitbit['body-weight'].iloc[0], 
		'body-fat': fitbit['body-fat'].iloc[0]
	}, index=[0]))

lifts = ['Bench Press', 'Military Press', 'Deadlift', 'Front Squat', 'Squat']

for lift in lifts:
	strong = strong.append(
		pandas.DataFrame({
			'Date': max_timestamp,
			'Exercise Name': lift,
			'lb': strong[strong['Exercise Name'] == lift]['lb'].iloc[-1],
			'Reps': 1
		}, index=[0])
	)
	strong = strong.append(
		pandas.DataFrame({
			'Date': min_timestamp,
			'Exercise Name': lift,
			'lb': strong[strong['Exercise Name'] == lift]['lb'].iloc[0],
			'Reps': 1
		}, index=[0])
	)

fitbit['body-weight-lbs'] = fitbit['body-weight'] * 2.20462
fitbit['lean-mass'] = fitbit['body-weight-lbs'] - fitbit['body-weight-lbs'] * (fitbit['body-fat'] / 100.0)
fitbit['fat-mass'] = fitbit['body-weight-lbs'] - fitbit['lean-mass']

fitbit['label'] = fitbit['dateTime'].apply(lambda x: x.strftime('%Y-%m-%d'))

fitbit['lean-mass'] += 10

caliper['lean-mass'] = caliper['weight'] - caliper['weight'] * (caliper['caliper-body-fat'] / 100.0)

strong['1RM'] = strong['lb'] / (1.0278 - (0.0278 * strong['Reps']))

p = figure(title="Body Composition", x_axis_type='datetime')

body_weight_rolling_avg = pandas.rolling_mean(fitbit['body-weight-lbs'], window=7)
lean_mass_rolling_avg = pandas.rolling_mean(fitbit['lean-mass'], window=7)
fat_mass_rolling_avg = pandas.rolling_mean(fitbit['fat-mass'], window=7)
bf_percent_rolling_avg = pandas.rolling_mean(fitbit['body-fat'], window=7)

p.circle(fitbit['dateTime'], body_weight_rolling_avg, color='#9999ff', legend="weight (lbs)")
p.circle(fitbit['dateTime'], lean_mass_rolling_avg, color='pink', legend="lean mass (lbs)")

p.legend.location = 'top_right'
p.legend.background_fill_alpha = 0.25
p.grid[0].ticker.desired_num_ticks = 15

p.circle(caliper['date'], caliper['weight'], color='blue')
p.circle(caliper['date'], caliper['lean-mass'], color='red')

p4 = figure(title="Fat mass", x_axis_type='datetime')
p4.circle(fitbit['dateTime'], fat_mass_rolling_avg, color='green', legend="fat mass (lbs)")

p5 = figure(title="Body fat percent", x_axis_type='datetime')
p5.circle(fitbit['dateTime'], bf_percent_rolling_avg, color='green', legend="body fat %")


lifts_to_plot = ['Bench Press', 'Military Press', 'Deadlift', 'Front Squat', 'Squat']
lift_colors = ['black', 'orange', 'blue', 'red', 'green']

lifts_to_plot = ['Front Squat', 'Deadlift']
lift_colors = ['orange', 'black']

p2 = figure(title="Lifts", x_axis_type='datetime')

for lift, color in zip(lifts_to_plot, lift_colors):
	lift_data = strong[strong['Exercise Name'] == lift]
	p2.circle(lift_data['Date'], lift_data['1RM'], color=color, legend=lift)

p2.legend.location = 'bottom_left'
p2.legend.background_fill_alpha = 0.25


lifts_to_plot = ['Bench Press', 'Military Press']
lift_colors = ['black', 'orange']

p3 = figure(title="Lifts", x_axis_type='datetime')

for lift, color in zip(lifts_to_plot, lift_colors):
	lift_data = strong[strong['Exercise Name'] == lift]
	p3.circle(lift_data['Date'], lift_data['1RM'], color=color, legend=lift)

p3.legend.location = 'bottom_left'
p3.legend.background_fill_alpha = 0.25

show(gridplot(p, p4, p2, p3, ncols=1, nrows=5, plot_width=800, plot_height=400))
