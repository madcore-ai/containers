import json
from jinja2 import Environment, FileSystemLoader

import pdfkit


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
            gutter_margin_horizontal = page["gutter-margin-horizontal"]
            gutter_margin_vertical = page["gutter-margin-vertical"]

            gutter_margin_left = '0.0mm'
            gutter_margin_right = '0.0mm'
            cls = 'no-gutters'
            if gutter_margin_horizontal != 0:
                gutter_margin_left = str(gutter_margin_horizontal) + 'mm'
                gutter_margin_right = str(gutter_margin_horizontal) + 'mm'


            gutter_margin_top = '0.0mm'
            gutter_margin_bottom = '0.0mm'
            if gutter_margin_vertical != 0:
                gutter_margin_top = str(gutter_margin_vertical) + 'mm'
                gutter_margin_bottom = str(gutter_margin_vertical) + 'mm'

            modules = page["modules"]
            skip_value = 0

            for i in range(1, rows + 1):
                html += "<div class='row " + cls + "'>"
                for j in range(1, columns + 1):
                    # html += "<div class='col-2'>"
                    if j > skip_value:
                        render_html = render_module(modules, i, j)
                        skip_value = render_html['skip_value']
                        # if render_html is not None:
                        html += str(render_html['html'])
                        html += "</div>"
                skip_value = 0
                html += "</div>"

        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("template/templateExampleGrid.html")
        template_vars = {"html": html, "debug": debug}
        # Render our file and create the PDF using our css style file
        html_out = template.render(template_vars)
        filename = 'template/render_template.html'
        f = open(filename, 'w+')
        f.write(html_out)
        f.close()
        options = {
            'page-size': page_size,
            'margin-top': gutter_margin_top,
            'margin-right': gutter_margin_right,
            'margin-bottom': gutter_margin_bottom,
            'margin-left': gutter_margin_left,
            # 'user-style-sheet':'/home/chizz/python/madcore/containers/pdfkit/bootstrap.min.css'
        }
        config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
        # css = '/home/chizz/python/madcore/containers/pdfkit/bootstrap.min.css'
        pdfkit.from_file('template/render_template.html', 'render_template.pdf', options=options, configuration=config)


def render_module(modules, i, j):
    colspan = 0
    skip_y = 0
    content = ''
    html = ''
    for module in modules:
        pos = module["pos"]
        pos_x = pos[0]
        pos_y = pos[1]
        kind = module["kind"]
        if pos_x == i and pos_y == j:
            if kind == "text":
                wrap = True
                if "wrap" in module:
                    wrap = module["wrap"]
                if not wrap:
                    if "colspan" in module:
                        colspan = module["colspan"]
                        skip = colspan - 1
                        skip_y = pos_y + skip
                    else:
                        colspan = (12 - pos_y) + 1
                        skip = colspan - 1
                        skip_y = pos_y + skip
                else:
                    if "colspan" in module:
                        colspan = module["colspan"]
                        skip = colspan - 1
                        skip_y = pos_y + skip

            if kind == "table":
                if "colspan" in module:
                    colspan = module["colspan"]
                    skip = colspan - 1
                    skip_y = pos_y + skip

            content = generate_module(module)
            break

    if colspan > 0:
        # cellappend = colspan*2 // when 6 columns
        cellappend = colspan
        html += "<div class='col-" + str(cellappend) + " debug'>"
    else:
        html += "<div class ='col-1 debug'>"

    html += content
    context = {
        'html': html,
        'skip_value': skip_y
    }
    return context


def generate_module(data):
    kind = data["kind"]
    if kind == "image":
        url = data["url"]
        return "<img class='img-responsive' src='" + url + "'>";


    elif kind == "text":
        text = data["text"]
        webfont = data["webfont"]
        webfontsize = data["webfontsize"]
        wrap = True
        wrap = data["wrap"]

        if wrap:
            return "<div style='font-family:" + webfont + "; font-size:" + webfontsize + "; word-wrap: break-word;'>" + text + "</div>"
        else:
            return "<div style='font-family:" + webfont + "; font-size:" + webfontsize + "'>" + text + "</div>"




    elif kind == "table":
        headers = data["headers"]
        datas = data["data"]
        cls = data["class"]
        webfont = data["webfont"]
        webfontsize = data["webfontsize"]
        table = "<table class='table " + cls + "' style='font-family:" + webfont + "; font-size:" + webfontsize + ";'>"
        for header in headers:
            table += "<th>" + header + "</th>"

        for data in datas:

            table += "<tr>"
            for item in data:
                table += "<td>" + item+ "</td>"
            table += "</tr>"

        table += "</table>"
        return table


if __name__ == "__main__":
    render()
