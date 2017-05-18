import pdfkit
import json
from jinja2 import Environment, FileSystemLoader
 

def hello():
    with open('mydata.json') as data_file:
        data = json.load(data_file)
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("mydata.html")
        template_vars = {"jsonData" : data}
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
        pdfkit.from_file('render.html', 'render.pdf', options=options)

if __name__ == "__main__":
    hello()
