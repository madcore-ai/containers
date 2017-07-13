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


class Domain_to_XLSX():

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

class Domain_to_Kafka():

    def __init__(self, domain, neo4j_conn, kafka_server, conf):
        self.worker = Worker(neo4j_conn, domain=domain)

        self.domain = domain
        self.topic = conf['doc']['type']
        self.producer = self.connect_kafka(kafka_server)
        for config in conf:
            self.kafka_handler(config)

    def connect_kafka(self, server):
        return KafkaProducer(bootstrap_servers=server)

    def kafka_handler(self, config):
        for query in config['queries']:
            data = self.worker.get_result(query['query'])
            if data:
                keys = data[0].keys()
                for v in data:
                    for k in keys:
                        self.producer.send(self.topic, k, v[k])


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
        query = "MATCH (d:Domain) WHERE d.name = 'bitnami.com' RETURN DISTINCT(d.name) as domain"
        return [x['domain'] for x in self.graph.data(query)]

    def process(self, verbose, transport):
        if verbose:
            for i in ['Worker']:
                logging.getLogger(i).setLevel(logging.INFO)

        for domain in self.all_domains:
            if transport == 'FILE':
                d = Domain_to_XLSX(domain, self.graph, self.output_path, self.conf['tabs'])
            elif transport == 'QUEUE':
                d = Domain_to_Kafka(domain, self.graph, 'kafka-kf.kafka.svc.cluster.local:9092', self.conf['tabs'])

