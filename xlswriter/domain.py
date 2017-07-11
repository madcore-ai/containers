from py2neo import Graph
from logger import Logger
from processor import Worker
from xlsxhandler import XlsHanler
import xlsxwriter
import os
import logging
import yaml
import sys


class Domain():

    def __init__(self, domain, neo4j_conn, output_path, conf):
        self.worker = Worker(neo4j_conn, domain=domain)
        self.xls_handler = XlsHanler(os.path.join(
            output_path, 'DOMAIN_{0}.xlsx'.format(domain)))

        self.domain = domain
        self.output_path = output_path
        for tab_config in conf:
            self.tab_handler(tab_config)

    def tab_handler(self, tab_config):
        row = 0
        col = 0
        gap = tab_config['gap']
        if tab_config['orientation'] == 'vertical':
            vt = True
        else:
            vt = False

        for query in tab_config['queries']:
            data = self.worker.get_result(query['query'])
            if not data:
                continue
            row, col = self.xls_handler.save_data_to_tab(
                tab_config['name'], data, row, col, vt, tab_config['autofit'])
            if vt:
                col += gap
                row = 2
            else:
                row += gap
                col = 2

    def in_json_format(self):
        pass

    def in_yaml_format(self):
        pass


class Domain_Handler(Logger):

    def __init__(self, output_path,
                 config_file='perspectives/DOMAIN.yaml',
                 neo4j_connection_string="bolt://localhost:7687",
                 neo4j_user="neo4j",
                 neo4j_password="neo4j"):
        super(self.__class__, self).__init__(self.__class__.__name__)
        self.graph = Graph(neo4j_connection_string,
                           user=neo4j_user,
                           password=neo4j_password)
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
        query = "MATCH (d:Domain) RETURN DISTINCT(d.name) as domain"
        return [x['domain'] for x in self.graph.data(query)]

    def process(self, verbose):
        if verbose:
            for i in ['Worker']:
                logging.getLogger(i).setLevel(logging.INFO)

        for domain in self.all_domains:
            d = Domain(domain, self.graph, self.output_path, self.conf['tabs'])
