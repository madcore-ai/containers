import json
from jinja2 import Environment, FileSystemLoader
from chart.datetimechart import DateTimeChart
import pdfkit


def hello():
    with open('mydata.json') as data_file:
        data = json.load(data_file)
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("mydata.html")

        if "chartactivity" in data["entity"]:
            chartactivity = data["entity"]["chartactivity"]
            chart = DateTimeChart(chartactivity[0]["name"],chartactivity[0]["color"],chartactivity[0]["values"])
            chart.plot()


        template_vars = {"jsonData" : data,"chart":"datetimevalue.png"}
        # Render our file and create the PDF using our css style file
        html_out = template.render(template_vars)
        filename = 'render.html'
        f = open(filename, 'w+')
        f.write(html_out)
        f.close()
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.5in',
            'margin-bottom': '0.75in',
            'margin-left': '0.5in'
        }
        config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        pdfkit.from_file('render.html', 'render.pdf', options=options, configuration=config)

if __name__ == "__main__":
    hello()
