from emailaddress_incoming_urls import EmailAddress_Incomming_Urls
from emailaddress_outgoing_urls import EmailAddress_Outgoing_Urls
from py2neo import Graph
import xlsxwriter
import os
import logging
from logger import Logger

class EmailAddress():

    def __init__(self, email_address, neo4j_conn, output_path ,sections):
        self.incomming_urls = EmailAddress_Incomming_Urls(neo4j_conn, email_address)
        self.outgoing_urls = EmailAddress_Outgoing_Urls(neo4j_conn, email_address)

        self.sections = sections
        self.email_address = email_address
        self.output_path = output_path
        self.data = self.__processor()

    def __processor(self):
        data = {}
        for section in self.sections:
            if section == 'UrlsIn':
                data[section] = []
                for v in self.incomming_urls.get_result():
                    data[section].append(v)
            elif section == 'UrlsOut':
                data[section] = []
                for v in self.outgoing_urls.get_result():
                    data[section].append(v)

        return data

    def write_to_xls(self):
        output_file = os.path.join(self.output_path, 'EMAIL_{0}.xlsx'.format(self.email_address))
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


class EmailAddress_Handler(Logger):

    def __init__(self, output_path, sections,
                 neo4j_connection_string="bolt://localhost:7687",
                 neo4j_user="neo4j",
                 neo4j_password="neo4j"):
        super(self.__class__, self).__init__(self.__class__.__name__)
        self.graph = Graph(neo4j_connection_string,
                           user=neo4j_user,
                           password=neo4j_password)
        self.sections = sections
        self.output_path = os.path.abspath(output_path)

    @property
    def all_emails(self):
        query = "MATCH (d:EmailAddress) RETURN DISTINCT(d.name) as email_address"
        return [x['email_address'] for x in self.graph.data(query)]

    def process(self, verbose):
        if verbose:
            for i in ['EmailAddress_Incomming_Urls', 'EmailAddress_Outgoing_Urls']:
                logging.getLogger(i).setLevel(logging.INFO)

        for email_address in self.all_emails:
            d = EmailAddress(email_address, self.graph, self.output_path,self.sections)
            d.write_to_xls()
