from py2neo import Graph
from logger import Logger
from processor import Worker
from xlsxhandler import XlsHanler
import xlsxwriter
import os
import logging
import yaml
import sys


class EmailAddress():

    def __init__(self, email_address, neo4j_conn, output_path, conf):
        self.worker = Worker(neo4j_conn, email_address=email_address)
        self.xls_handler = XlsHanler(os.path.join(
            output_path, 'EMAIL_{0}.xlsx'.format(email_address)))

        self.email_address = email_address
        self.output_path = output_path
        for tab_config in conf:
            self.tab_handler(tab_config)

    def tab_handler(self, tab_config):
        row = 2
        col = 2
        gap = tab_config['gap']
        if tab_config['orientation'] == 'horizontal':
            hoz = True
        else:
            hoz = False

        if tab_config['autofit'] == 'True':
            af = True
        else:
            af = False

        for query in tab_config['queries']:
            data = self.worker.get_result(query['query'])
            if not data:
                continue
            row, col = self.xls_handler.save_data_to_tab(
                tab_config['name'], data, row, col, hoz, af)
            if hoz:
                col += gap
                row = 2
            else:
                row += gap
                col = 2


class EmailAddress_Handler(Logger):

    def __init__(self, output_path,
                 config_file='perspectives/EMAIL.yaml',
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
    def all_emails(self):
        query = "MATCH (d:EmailAddress) RETURN DISTINCT(d.name) as email_address"
        return [x['email_address'] for x in self.graph.data(query)]

    def process(self, verbose):
        if verbose:
            for i in ['Worker']:
                logging.getLogger(i).setLevel(logging.INFO)

        for email_address in self.all_emails:
            d = EmailAddress(email_address, self.graph,
                             self.output_path, self.conf['tabs'])
