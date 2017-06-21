from neo4j.v1 import GraphDatabase
import re
import validators
from lxml import html
from flanker.addresslib import address

class F2n(object):

    def __init__(self, activate_processors_list,
                 neo4j_connection_string="bolt://localhost:7687",
                 neo4j_auth=("neo4j", "password")):

        self.driver = GraphDatabase.driver(
            neo4j_connection_string, auth=neo4j_auth)
        self.processors = activate_processors_list

    @staticmethod
    def w2n_EmailAddress_SENT_Message(tx, email, message):
        tx.run("MERGE (user:EmailAddress {name: $email_address, display_name: $email_name}) "
               "MERGE (email: Message {id: $message_id, content: $message_content}) "
               "MERGE (user)-[:SENT]->(email)",
               email_address=email['address'],
               email_name=email['name'],
               message_id=message['id'],
               message_content=message['content'])

    @staticmethod
    def w2n_Message_TO_EmailAddress(tx, message, email):
        tx.run("MERGE (email: Message {id: $message_id, content: $message_content}) "
               "MERGE (user:EmailAddress {name: $email_address, display_name: $email_name}) "
               "MERGE (email)-[:TO]->(user)",
               message_id=message['id'],
               message_content=message['content'],
               email_address=email['address'],
               email_name=email['name'])

    @staticmethod
    def w2n_Message_CC_EmailAddress(tx, message, email):
        tx.run("MERGE (email: Message {id: $message_id, content: $message_content}) "
               "MERGE (user:EmailAddress {name: $email_address, display_name: $email_name}) "
               "MERGE (email)-[:CC]->(user)",
               message_id=message['id'],
               message_content=message['content'],
               email_address=email['address'],
               email_name=email['name'])

    @staticmethod
    def w2n_Message_CONTAINS_Url(tx, message, url):
        tx.run("MERGE (email: Message {id: $message_id, content: $message_content}) "
               "MERGE (url: Url {full_link: $url_full, scheme: $scheme, sub_domain: $sub, domain: $domain, document: $document }) "
               "MERGE (email)-[:CONTAINS]->(url)",
               message_id=message['id'],
               message_content=message['content'],
               url_full=url['full'],
               scheme=url['scheme'],
               sub='wwww',
               domain=url['domain'],
               document=url['document'])

    @staticmethod
    def w2n_Url_BELONGS_TO_Domain(tx, url, domain):
        tx.run("MERGE (url: Url {full_link: $url_full, scheme: $scheme, sub_domain: $sub, domain: $domain, document: $document }) "
               "MERGE (domain: Domain {name: $original_domain}) "
               "MERGE (url)-[:BELONGS_TO]->(domain)",
               url_full=url['full'],
               scheme=url['scheme'],
               sub='wwww',
               domain=url['domain'],
               document=url['document'],
               original_domain=domain)

    @staticmethod
    def w2n_EmailAddress_BELONGS_TO_Domain(tx, email, domain):
        tx.run("MERGE (user:EmailAddress {name: $email_address, display_name: $email_name}) "
               "MERGE (domain: Domain {name: $original_domain}) "
               "MERGE (url)-[:BELONGS_TO]->(domain)",
               email_address=email['address'],
               email_name=email['name'],
               original_domain=domain)

    @staticmethod
    def w2n_Url_POSTED_BY_EmailAddress(tx, url, email):
        tx.run("MERGE (user:EmailAddress {name: $email_address, display_name: $email_name}) "
               "MERGE (url: Url {full_link: $url_full, scheme: $scheme, sub_domain: $sub, domain: $domain, document: $document }) "
               "MERGE (url)-[:POSTED_BY]->(user)",
               url_full=url['full'],
               scheme=url['scheme'],
               sub='wwww',
               domain=url['domain'],
               document=url['document'],
               email_address=email['address'],
               email_name=email['name'])

    @staticmethod
    def extract_url_from_text_plain(string):
        regex = r'('
        regex += r'(?:(https?|s?ftp):\/\/)?'
        regex += r'(?:www\.)?'
        regex += r'('
        regex += r'(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)'
        regex += r'([A-Z0-9][A-Z0-9-]{0,61}\.[A-Z]{2,6})'
        regex += r'|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        regex += r')'
        regex += r'(?::(\d{1,5}))?'
        regex += r'(?:(\/\S+)*)'
        regex += r')'

        find_urls_in_string = re.compile(regex, re.IGNORECASE)
        url = find_urls_in_string.search(string)

        if url is not None and url.group(0) is not None:
            return url.groups()
        return (None, None, None, None, None, None)

    @staticmethod
    def extract_url_from_text_html(string):
        result = set()
        tree = html.fromstring(string)
        for value in tree.xpath("//@href"):
            if validators.url(value):
                result.add(value)
        return result

    def __url01_process_mime_part(self, part):
        result = set()
        if part.body:
            if part.content_type.main == 'text':
                if part.content_type.sub == 'plain':
                    for line in part.body.splitlines():
                        data, _, _, _, _, _ = self.extract_url_from_text_plain(line)
                        if data:
                            result.add(data)
                if part.content_type.sub == 'html':
                    tmp = self.extract_url_from_text_html(part.body)
                    result.update(tmp)
        else:
            for p in part.parts:
                data_list = self.__url01_process_mime_part(p)
                if data_list:
                    result.update(data_list)

        # print 'in ', result
        return result

    def map01(self, msg):
        # mapping of email interactions, ADDRESS_HEADERS = ('From', 'To',
        # 'Delivered-To', 'Cc', 'Bcc', 'Reply-To')
        with self.driver.session() as session:
            self.count+=2
            session.write_transaction(self.w2n_EmailAddress_SENT_Message, self.sender, self.message)
            session.write_transaction(self.w2n_EmailAddress_BELONGS_TO_Domain, self.sender, self.sender['address'].split('@')[-1])
            for to_email in self.receivers['to']:
                self.count+=2
                session.write_transaction(self.w2n_Message_TO_EmailAddress, self.message, to_email)
                session.write_transaction(self.w2n_EmailAddress_BELONGS_TO_Domain, to_email, to_email['address'].split('@')[-1])
            for cc_email in self.receivers['cc']:
                self.count+=2
                session.write_transaction(self.w2n_Message_CC_EmailAddress, self.message, cc_email)
                session.write_transaction(self.w2n_EmailAddress_BELONGS_TO_Domain, cc_email, cc_email['address'].split('@')[-1])




    def url01(self, msg):
        # mappings of URL in headers or message bodies

        result = self.__url01_process_mime_part(msg)
        # print result
        for data in result:
            if validators.url(data):
                _, scheme, full_domain, domain, _, document = self.extract_url_from_text_plain(
                    data)
                url = {
                    'full': str(data),
                    'scheme': str(scheme),
                    'domain': str(domain),
                    'document': str(document)
                }
                with self.driver.session() as session:
                    self.count+=2
                    session.write_transaction(self.w2n_Message_CONTAINS_Url, self.message, url)
                    session.write_transaction(self.w2n_Url_BELONGS_TO_Domain, url, url['domain'])

    def ip01(self, msg):
        ip_found = re.findall(
            r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', msg.to_string())
        pass

    def process(self, msg):
        # count how many time connect to neo4j
        self.count = 0
        # initialize message basic information
        self.message = {
            'id': str(msg.message_id),
            'content': msg.to_string()
        }

        sender = address.parse(msg.headers.get('From'))
        self.sender = {
            'address': sender.address,
            'name': sender.display_name
        }
        self.receivers = {
            'to': [],
            'cc': [],
            'bcc': []
        }
        for value in address.parse_list(msg.headers.get('To')):
            tmp = {
                'address': value.address,
                'name': value.display_name
            }
            self.receivers['to'].append(tmp)
        for value in address.parse_list(msg.headers.get('CC')):
            tmp = {
                'address': value.address,
                'name': value.display_name
            }
            self.receivers['cc'].append(tmp)

        for func in self.processors:
            getattr(self, func)(msg)

        print 'connections ', self.count
