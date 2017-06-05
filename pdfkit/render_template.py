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
        debug = entity["debug"]
        page_size = "A4"

        if entity["page-size"] != "":
            page_size = entity["page-size"]

        html = ''
        for page in pages:
            columns = page["max-x"]
            rows = page["max-y"]
            gutter_margin_left = page["gutter-margin-left"]
            gutter_margin_right = page["gutter-margin-right"]

            if gutter_margin_left ==0 and gutter_margin_right ==0:
                gutter_margin_left = '0.0in'
                gutter_margin_right = '0.0in'
                cls = 'no-gutters'

            modules = page["modules"]
            skip_value = 0

            for i in range(1,rows+1):
                html += "<div class='row "+cls+"'>"
                for j in range(1,columns+1):
                    # html += "<div class='col-2'>"
                    if j > skip_value:
                        render_html = render_module(modules,i,j)
                        skip_value = render_html['skip_value']
                        # if render_html is not None:
                        html += str(render_html['html'])
                        html += "</div>"
                skip_value=0
                html += "</div>"



        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("templateExampleGrid.html")
        template_vars = {"html" : html,"debug":debug}
        # Render our file and create the PDF using our css style file
        html_out = template.render(template_vars)
        filename = 'render_template.html'
        f = open(filename, 'w+')
        f.write(html_out)
        f.close()
        options = {
            'page-size': page_size,
            'margin-top': '0.0mm',
            'margin-right': '0.0mm',
            'margin-bottom': '0.0mm',
            'margin-left': '0.0mm',
            # 'user-style-sheet':'/home/chizz/python/madcore/containers/pdfkit/bootstrap.min.css'
        }
        config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
        # css = '/home/chizz/python/madcore/containers/pdfkit/bootstrap.min.css'
        pdfkit.from_file('render_template.html', 'render_template.pdf', options=options, configuration=config)




def render_module(modules,i,j):
    colspan = 0
    skip_y = 0
    content = ''
    html = ''
    for module in modules:
        pos = module["pos"]
        pos_x= pos[0]
        pos_y= pos[1]
        kind = module["kind"]
        if pos_x==i and pos_y==j:
           if kind == "text":
            wrap = True
            if "wrap" in module:
                wrap = module["wrap"]
            if not wrap:
                if "colspan" in module:
                    colspan = module["colspan"]
                    skip = colspan-1
                    skip_y = pos_y+skip
                else:
                    colspan = (12 - pos_y)+1
                    skip = colspan-1
                    skip_y = pos_y+skip
            else:
                if "colspan" in module:
                    colspan = module["colspan"]
                    skip = colspan-1
                    skip_y = pos_y+skip

           content = generate_module(module)
           break

    if colspan > 0:
        # cellappend = colspan*2 // when 6 columns
        cellappend = colspan
        html += "<div class='col-"+str(cellappend)+" debug'>"
    else:
        html += "<div class ='col-1 debug'>"

    html+=content
    context = {
        'html':html,
        'skip_value': skip_y
    }
    return context





def generate_module(data):
    kind = data["kind"]
    if kind == "image":
        url = data["url"]
        return "<img class='img-responsive' src='"+url+"'>";


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
