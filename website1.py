from flask import Flask,render_template,request

app = Flask(__name__)

@app.route('/plot')
def plot():
    return render_template("plot.html")

@app.route('/candlestick',methods=['POST','GET'])
def candlestick():
    if request.method == 'POST':
        try:
            co = request.form['co']
            strt = request.form['start']
            end = request.form['end']

            import pandas_datareader.data as web
            from datetime import datetime as dt

            df=web.DataReader(co, "iex", start=strt, end=end)

            def inc_dec(c,o):
                if c > o:
                    value = "Increase"
                elif c < o:
                    value = "Decrease"
                else:
                    value = "Equal"
                return value

            df["status"] = [inc_dec(c,o) for c, o in zip(df.close,df.open)]
            df["middle"] = [(c+o)/2 for c, o in zip(df.close,df.open)]
            df["height"] = abs(df.close - df.open)
            df.index = df.index.map(lambda x: dt.strptime(x,"%Y-%m-%d"))

            from bokeh.plotting import figure
            from bokeh.models import DatetimeTickFormatter
            import numpy as np
            from bokeh.embed import components
            from bokeh.resources import CDN

            p = figure(x_axis_type="datetime", width = 1000, height = 300, sizing_mode = 'scale_width')
            p.title.text = "Candlestick graph"
            p.title.align = "center"
            p.title.text_font_size = "16pt"
            p.title.text_font_style = "bold"

            p.xaxis.axis_label = "Date"
            p.xaxis.axis_label_text_font_style = "bold"
            p.xaxis.axis_label_text_font_size = "12pt"
            p.xaxis[0].formatter = DatetimeTickFormatter(days = ['%e %B %Y'])
            p.xgrid.grid_line_alpha = 0.7

            p.yaxis.axis_label = "Price"
            p.yaxis.axis_label_text_font_style = "bold"
            p.yaxis.axis_label_text_font_size = "12pt"

            hours = 12*60*60*1000

            p.segment(df.index, df.high, df.index, df.low, color = "black")

            p.rect(df.index[df.status == "Increase"], df.middle[df.status == "Increase"],
                   hours, df.height[df.status == "Increase"], line_color = "black", fill_color="#80ff80")

            p.rect(df.index[df.status == "Decrease"], df.middle[df.status == "Decrease"],
                   hours, df.height[df.status == "Decrease"], line_color = "black", fill_color="#ff6666")

            script1 , div = components(p)

            cdn_js = CDN.js_files
            cdn_css = CDN.css_files
            return render_template("candlestick.html",
            script1 = script1,
            div1 = div,
            cdn_css = cdn_css[0],
            cdn_js = cdn_js[0])
        except KeyError:
            return render_template("plot.html", error = "Try some other company.")

@app.route('/')
def layout():
    return render_template("layout.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
