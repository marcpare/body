import numpy as np

from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file

x = np.linspace(0, 4*np.pi, 100)
y = np.sin(x)

TOOLS = "pan"

p1 = figure(title="Example", tools=TOOLS)

p1.circle(x, y, legend="sin(x)")

p2 = figure(title="Another example", tools=TOOLS)

p2.circle(x, y, legend="sin(x)")

# output_file("legend.html", title="my first example")

show(gridplot(p1, p2, ncols=2, plot_width=400, plot_height=400))



# Read bodyfat.csv
# Plot weight, leanmass

# Read fitbit.csv
# Overlay weight, leanmass on same plot

