import json
from jinja2 import Environment, FileSystemLoader
from chart.datetimechart import DateTimeChart
import pdfkit
import producer


def render():
    with open('templateExampleGrid.json') as data_file:
        data = json.load(data_file)

        entity = data["entity"]
        pages = entity["pages"]

        html = ''
        for page in pages:
            columns = page["max-x"]
            rows = page["max-y"]
            gutter_margin_left = page["gutter-margin-left"]
            gutter_margin_right = page["gutter-margin-right"]

            modules = page["modules"]


            for i in range(1,rows+1):
                html += "<div class='row'>";
                for j in range(1,columns+1):
                    html += "<div class='col'>"
                    render_html = render_module(modules,i,j)
                    if render_html is not None:
                        html += str(render_html)
                    html += "</div>"
                html += "</div>"



        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("templateExampleGrid.html")
        template_vars = {"html" : html}
        # Render our file and create the PDF using our css style file
        html_out = template.render(template_vars)
        filename = 'render_template.html'
        f = open(filename, 'w+')
        f.write(html_out)
        f.close()
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.5in',
            'margin-bottom': '0.75in',
            'margin-left': '0.5in',
            # 'user-style-sheet':'/home/chizz/python/madcore/containers/pdfkit/bootstrap.min.css'
        }
        config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
        # css = '/home/chizz/python/madcore/containers/pdfkit/bootstrap.min.css'
        pdfkit.from_file('render_template.html', 'render_template.pdf', options=options, configuration=config)




def render_module(modules,i,j):
    for module in modules:
        pos = module["pos"]
        pos_x= pos[0]
        pos_y= pos[1]

        if pos_x==i and pos_y==j:
           return generate_module(module)



def generate_module(data):
    kind = data["kind"]
    if kind == "image":
        url = data["url"]
        return "<img src='"+url+"'>";


    elif kind == "text":
        text = data["text"]
        webfont = data["webfont"]
        webfontsize = data["webfontsize"]

        return "<div style='font-family:"+webfont+"; font-size:"+webfontsize+"'>"+text+"</div>"




    elif kind == "table":
        headers = data["headers"]
        datas = data["data"]
        table = '<table>';
        for header in headers:
            table += "<th>"+header+"</th>"

        for data in datas:

            table += "<tr>"
            table += "<td>"+data["name"]+"</td>"
            table += "<td>"+data["location"]+"</td>"
            table += "<td>"+data["date"]+"</td>"
            table += "</tr>"

        table += "</table>"
        return  table









if __name__ == "__main__":
    render()
