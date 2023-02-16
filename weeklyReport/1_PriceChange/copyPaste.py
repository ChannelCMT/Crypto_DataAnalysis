from bokeh.models import BoxAnnotation
from bokeh.models import ColumnDataSource, Label, LabelSet, Range1d, Arrow, OpenHead
from bokeh.layouts import column
from math import pi
from bokeh.plotting import figure
from bokeh.io import output_notebook,show
from bokeh.resources import INLINE
import bokeh.io
from bokeh import *
bokeh.io.output_notebook(INLINE)

inc = dataCoin2.close > dataCoin2.open
dec = dataCoin2.open > dataCoin2.close

w = 12*60*60*50

## Candlestick chart
candlestick = figure(x_axis_type="datetime", plot_width=800, plot_height=500, title = "ETH", toolbar_location=None)

candlestick.segment(dataCoin2.index[inc], dataCoin2.high[inc], dataCoin2.index[inc], dataCoin2.low[inc], color="green")
candlestick.segment(dataCoin2.index[dec], dataCoin2.high[dec], dataCoin2.index[dec], dataCoin2.low[dec], color="red")

candlestick.vbar(dataCoin2.index[inc], w, dataCoin2.open[inc], dataCoin2.close[inc],
         fill_color="green", line_color="green")

candlestick.vbar(dataCoin2.index[dec], w, dataCoin2.open[dec], dataCoin2.close[dec],
         fill_color="red", line_color="red")

Now = dataCoin2.index[-1]
x1Days = dataCoin2.index[-1]-timedelta(days=1)
x3Days = dataCoin2.index[-1]-timedelta(days=3)
x5Days = dataCoin2.index[-1]-timedelta(days=5)
x7Days = dataCoin2.index[-1]-timedelta(days=7)


candlestick.add_layout(Arrow(x_start=x1Days, x_end=Now, y_start=dataCoin2.close[x1Days], y_end=dataCoin2.close[Now],
                     end=OpenHead(line_color="orange", line_width=2, line_alpha=1),
                     line_color="orange", line_width=2, line_alpha=1, line_dash='dashed'
                    ))
citation1 = Label(x=x1Days, y=dataCoin2.close[x1Days], x_units='data', y_units='data',
                 text=pctChangeDfT.loc['eth_pctChange']['1Day'], render_mode='css',
                 border_line_color='orange', border_line_alpha=1.0,
                 background_fill_color='orange', background_fill_alpha=1.0,
                 text_color="white")

candlestick.add_layout(Arrow(x_start=x3Days, x_end=Now, y_start=dataCoin2.close[x3Days], y_end=dataCoin2.close[Now],
                     end=OpenHead(line_color="olive", line_width=2, line_alpha=1),
                     line_color="olive", line_width=2, line_alpha=1, line_dash='dashed'
                    ))

citation3 = Label(x=x3Days, y=dataCoin2.close[x3Days], x_units='data', y_units='data',
                 text=pctChangeDfT.loc['eth_pctChange']['3Day'], render_mode='css',
                 border_line_color='olive', border_line_alpha=1.0,
                 background_fill_color='olive', background_fill_alpha=1.0,
                 text_color="white")

candlestick.add_layout(Arrow(x_start=x5Days, x_end=Now, y_start=dataCoin2.close[x5Days], y_end=dataCoin2.close[Now],
                     end=OpenHead(line_color="lime", line_width=2, line_alpha=1),
                     line_color="lime", line_width=2, line_alpha=1, line_dash='dashed'
                    ))

citation5 = Label(x=x5Days, y=dataCoin2.close[x5Days], x_units='data', y_units='data',
                 text=pctChangeDfT.loc['eth_pctChange']['5Day'], render_mode='css',
                 border_line_color='lime', border_line_alpha=1.0,
                 background_fill_color='lime', background_fill_alpha=1.0,
                 text_color="white")

candlestick.add_layout(Arrow(x_start=x7Days, x_end=Now, y_start=dataCoin2.close[x7Days], y_end=dataCoin2.close[Now],
                     end=OpenHead(line_color="cyan", line_width=2, line_alpha=1),
                     line_color="cyan", line_width=2, line_alpha=1, line_dash='dashed'
                    ))

citation7 = Label(x=x7Days, y=dataCoin2.close[x7Days], x_units='data', y_units='data',
                 text=pctChangeDfT.loc['eth_pctChange']['7Day'], render_mode='css',
                 border_line_color='cyan', border_line_alpha=1.0,
                 background_fill_color='cyan', background_fill_alpha=1.0,
                 text_color="white")

candlestick.add_layout(citation1)
candlestick.add_layout(citation3)
candlestick.add_layout(citation5)
candlestick.add_layout(citation7)
show(candlestick)