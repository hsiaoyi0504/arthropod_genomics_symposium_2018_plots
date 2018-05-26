from git import Git
from os.path import join, dirname, abspath
from datetime import datetime, timezone
import pandas as pd
from bokeh.plotting import figure
from bokeh.io import export_png
from bokeh.models.tickers import FixedTicker
import numpy as np

repo_dir = join(dirname(abspath(__file__)), 'genomics-workspace')


def get_date(line):
    return line.split('\t')[0]


def convert_date(date_string):
    return datetime.strptime(date_string, '%a %b %d %H:%M:%S %Y %z').replace(tzinfo=timezone.utc)


def bin_date(date):
    return str(date.year) + 'Q' + str(int(date.month/4) + 1)


g = Git(repo_dir)
logs = g.log('--after=2012-08-01', '--no-merges', '--pretty=format:%ad%x09%s', '--branches')  # date <tab> commit subject
lines = logs.split('\n')
dates = list(map(get_date, lines))  # dates are in this format: Wed May 23 09:34:01 2018 -0400
dates = list(map(convert_date, dates))

df = pd.DataFrame({'date': dates})
df['year/quarter'] = df['date'].apply(bin_date)
data = df['year/quarter'].value_counts().sort_index()
index = data.index.tolist()
y = data.tolist()
x = range(len(data))
p = figure(title='Development Activities', x_axis_label='Time', y_axis_label='Number of commits', x_range=(0, len(data) - 2), y_range=(0, max(y)))
p.line(x, y)
label_overrides = {}
for i, ind in zip(x, index):
    label_overrides[i] = ind
p.xaxis.major_label_overrides = label_overrides
p.title.align = 'center'
p.xaxis.ticker = FixedTicker(ticks=list(range(len(data) - 1)))
p.xaxis.major_label_orientation = np.pi / 4
p.toolbar.logo = None
p.toolbar_location = None
export_png(p, 'development_activities.png')
