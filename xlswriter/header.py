from py2neo import Graph
from logger import Logger
from processor import Worker
from xlsxhandler import XlsHanler
from kafka import KafkaProducer
import xlsxwriter
import os
import logging
import yaml
import sys

class Header_to_XLSX():

    def __init__(self, message_id, neo4j_conn, output_path, conf):
        self.worker = Worker(neo4j_conn, message_id=message_id)
        self.xls_handler = XlsHanler(os.path.join(
            output_path, 'HEADER_{0}.xlsx'.format(message_id)))

        self.message_id = message_id
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
            title = query['title']
            if not data:
                continue
            row, col = self.xls_handler.save_data_to_tab(
                tab_config['name'], title, data, row, col, vt, tab_config['autofit'])
            if vt:
                col += gap
                row = 0
            else:
                row += gap
                col = 0

class Header_Handler(Logger):

    def __init__(self, output_path,
                 config_file='perspectives/HEADER.yaml',
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
    def all_message_id(self):
        query = "MATCH (m:Message) RETURN DISTINCT(m.message_id) as message_id"
        return [x['message_id'] for x in self.graph.data(query)]

    def process(self, verbose, transport):
        if verbose:
            for i in ['Worker']:
                logging.getLogger(i).setLevel(logging.INFO)

        for message_id in self.all_message_id:
            if transport == 'FILE':
                d = Header_to_XLSX(message_id, self.graph, self.output_path, self.conf['tabs'])
            # elif transport == 'QUEUE':
            #     d = Domain_to_Kafka(message_id, self.graph, 'localhost:9092', self.conf['tabs'])