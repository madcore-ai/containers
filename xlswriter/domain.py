from domain_urls import Domain_Urls
from domain_emailaddresses import Domain_EmailAddresses
from domain_schemes import Domain_Schemes
from domain_subdomains import Domain_SubDomains
from py2neo import Graph
import xlsxwriter
import os
import logging
from logger import Logger
import yaml
import sys


class Worker(Logger):

    def __init__(self, conn, domain):
        super(self.__class__, self).__init__(self.__class__.__name__)
        self.conn = conn
        self.domain = domain

    def build_query(self, query):
        return query.format(self.domain)

    def __query(self, query):
        self.logger.info(query)
        return self.conn.data(query)

    def get_result(self, query):
        query = self.build_query(query)
        return self.__query(query)

class XlsHanler():
    def __init__(self, filename):
        self.workbook = xlsxwriter.Workbook(filename)
        self.bold = self.workbook.add_format({'bold': True})

    def get_tab_by_name(self, tab_name):
        if self.workbook.get_worksheet_by_name(tab_name):
            return self.workbook.get_worksheet_by_name(tab_name)
        else:
            return self.workbook.add_worksheet(tab_name)

    def save_data_to_tab(self, tab_name, data, row_start, col_start, horizontal=False):
        row = row_start
        col = col_start
        worksheet = self.get_tab_by_name(tab_name)
        keys = data[0].keys()
        for k in keys:
            worksheet.write(row, col, k, self.bold)
            if horizontal:
                row += 1
            else:
                col += 1
        if horizontal:
            row = row_start
            col = col_start + 1
        else:
            row = row_start + 1
            col = col_start
        for v in data:
            for k in keys:
                worksheet.write_string(row, col, v[k])
                if horizontal:
                    row += 1
                else:
                    col += 1
            if horizontal:
                row = row_start
                col += 1
            else:
                col = col_start
                row += 1

        return row, col


class Domain():

    def __init__(self, domain, neo4j_conn, output_path, sections, conf):
        # self.urls = Domain_Urls(neo4j_conn, domain)
        # self.email_addresses = Domain_EmailAddresses(neo4j_conn, domain)
        # self.schemes = Domain_Schemes(neo4j_conn, domain)
        # self.sub_domains = Domain_SubDomains(neo4j_conn, domain)
        self.worker = Worker(neo4j_conn, domain)
        self.xls_handler = XlsHanler(os.path.join(output_path, 'DOMAIN_{0}.xlsx'.format(domain)))

        self.sections = sections
        self.domain = domain
        self.output_path = output_path
        for tab_config in conf:
            self.tab_handler(tab_config)
        # self.data = self.__processor()

    def tab_handler(self, tab_config):
        row = 2
        col = 2
        gap = tab_config['gap']

        for query in tab_config['queries']:
            data = self.worker.get_result(query['query'])
            row, _ = self.xls_handler.save_data_to_tab(tab_config['name'], data, row, col)
            row += gap



    def __processor(self):
        data = {}
        for section in self.sections:
            if section == 'EmailAddresses':
                data[section] = []
                for v in self.email_addresses.get_result():
                    data[section].append(v)
            elif section == 'Urls':
                data[section] = []
                for v in self.urls.get_result():
                    data[section].append(v)
            elif section == 'Schemes':
                data[section] = []
                for v in self.schemes.get_result():
                    data[section].append(v)
            elif section == 'SubDomains':
                data[section] = []
                for v in self.sub_domains.get_result():
                    data[section].append(v)

        return data

    def write_to_xls(self):
        output_file = os.path.join(
            self.output_path, 'DOMAIN_{0}.xlsx'.format(self.domain))
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


class Domain_Handler(Logger):

    def __init__(self, output_path, sections,
                 config_file=None,
                 neo4j_connection_string="bolt://localhost:7687",
                 neo4j_user="neo4j",
                 neo4j_password="neo4j"):
        super(self.__class__, self).__init__(self.__class__.__name__)
        self.graph = Graph(neo4j_connection_string,
                           user=neo4j_user,
                           password=neo4j_password)
        self.sections = sections
        self.output_path = os.path.abspath(output_path)
        if config_file:
            with open(config_file, 'r') as f:
                try:
                    self.conf = yaml.load(f)
                except Exception as e:
                    raise e
                    sys.exit(1)


    @property
    def all_domains(self):
        query = "MATCH (d:Domain) WHERE d.name = 'bitnami.com' RETURN DISTINCT(d.name) as domain"
        return [x['domain'] for x in self.graph.data(query)]

    def process(self, verbose):
        if verbose:
            for i in ['Domain_Urls', 'Domain_EmailAddresses', 'Domain_Schemes', 'Domain_SubDomains']:
                logging.getLogger(i).setLevel(logging.INFO)

        for domain in self.all_domains:
            d = Domain(domain, self.graph, self.output_path, self.sections, self.conf['tabs'])
            # d.write_to_xls()
