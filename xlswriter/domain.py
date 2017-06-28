from domain_urls import Domain_Urls
from domain_emailaddresses import Domain_EmailAddresses

from py2neo import Graph
import xlsxwriter


class Domain():

    def __init__(self, domain, neo4j_conn, sections=[]):
        self.urls = Domain_Urls(neo4j_conn, domain)
        self.email_addresses = Domain_EmailAddresses(neo4j_conn, domain)

        self.sections = sections
        self.domain = domain
        self.data = self.__processor()

    def __processor(self):
        data = {}
        for section in self.sections:
            if section == 'Email Addresses':
                data[section] = []
                for v in self.email_addresses.get_result():
                    data[section].append(v)
            elif section == 'Urls':
                data[section] = []
                for v in self.urls.get_result():
                    data[section].append(v)
        return data

    def write_to_xls(self):
        output_file = 'DOMAIN_{0}.xlsx'.format(self.domain)
        workbook = xlsxwriter.Workbook(output_file)
        for section in self.data.keys():
            row = 0
            col = 0
            worksheet = workbook.add_worksheet(section)
            if self.data[section]:
                keys = self.data[section][0].keys()
                for k in keys:
                    worksheet.write(row, col, k)
                    col += 1
                col = 0
                row = 1
                for v in self.data[section]:
                    for k in keys:
                        worksheet.write_string(row, col, v[k])
                        col += 1
                    col = 0
                    row += 1

        workbook.close()

    def in_json_format(self):
        pass

    def in_yaml_format(self):
        pass


class Domain_Handler():

    def __init__(self, neo4j_connection_string="bolt://localhost:7687",
                 neo4j_user="neo4j",
                 neo4j_password="neo4j"):
        self.graph = Graph(neo4j_connection_string,
                           user=neo4j_user,
                           password=neo4j_password)

    @property
    def all_domains(self):
        query = "MATCH (d:Domain) RETURN DISTINCT(d.name) as domain"
        return [x['domain'] for x in self.graph.data(query)]

    def process(self):
        for domain in self.all_domains:
            d = Domain(domain, self.graph ,['Email Addresses', 'Urls'])
            d.write_to_xls()