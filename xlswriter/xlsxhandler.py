import xlsxwriter
import yaml


class XlsHanler():

    def __init__(self, output_file, theme_file='formats/mini.yaml'):
        self.workbook = xlsxwriter.Workbook(output_file)
        with open(theme_file, 'r') as f:
            conf = yaml.load(f)
        self.header_format = self.workbook.add_format(conf.get('header'))
        self.cell_format = self.workbook.add_format(conf.get('cell'))

    def get_tab_by_name(self, tab_name):
        if self.workbook.get_worksheet_by_name(tab_name):
            return self.workbook.get_worksheet_by_name(tab_name)
        else:
            return self.workbook.add_worksheet(tab_name)

    def save_data_to_tab(self, tab_name, data, row_start, col_start, vertical=False, autofit=False):
        row = row_start
        col = col_start
        worksheet = self.get_tab_by_name(tab_name)
        keys = data[0].keys()
        max_column_width = 0
        for k in keys:
            if len(k) > max_column_width:
                max_column_width = len(k)
            worksheet.write(row, col, k, self.header_format)
            if vertical:
                row += 1
            else:
                col += 1
        if vertical:
            row = row_start
            col = col_start + 1
        else:
            row = row_start + 1
            col = col_start
        for v in data:
            for k in keys:
                if len(v[k]) > max_column_width:
                    max_column_width = len(v[k])
                worksheet.write_string(row, col, v[k])
                if vertical:
                    row += 1
                else:
                    col += 1
            if vertical:
                row = row_start
                col += 1
            else:
                col = col_start
                row += 1
        if autofit:
            worksheet.set_column(row, col, max_column_width)
            print row, col, max_column_width

        return row, col

