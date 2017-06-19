from neo4j.v1 import GraphDatabase
import re


class F2n(object):

    def __init__(self, activate_processors_list,
                 neo4j_connection_string="bolt://localhost:7687",
                 neo4j_auth=("neo4j", "password")):

        self.driver = GraphDatabase.driver(
            neo4j_connection_string, auth=neo4j_auth)
        self.processors = activate_processors_list

    def map01(self, msg):
        # mapping of email interactions, ADDRESS_HEADERS = ('From', 'To',
        # 'Delivered-To', 'Cc', 'Bcc', 'Reply-To')
        pass

    def url01(self, msg):
        # mappings of URL in headers or message bodies
        pass

    def ip01(self, msg):
        ip_found = re.findall(
            r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', msg.to_string())
        pass

    def process(self, msg):
        for func in self.processors:
            getattr(self, func)(msg)
