from py2neo import Graph
import re
import validators
from lxml import html
from flanker.addresslib import address
import tldextract
import yaml
import logging
import logging.config
import email.utils
import time
import datetime
import os


class F2n(object):

    def __init__(self, activate_processors_list,
                 datadir,
                 neo4j_connection_string="bolt://localhost:7687",
                 neo4j_user="neo4j",
                 neo4j_password="neo4j"):

        self.graph = Graph(neo4j_connection_string,
                           user=neo4j_user,
                           password=neo4j_password)
        self.processors = activate_processors_list
        self.logs_dir = os.path.join(datadir, 'logs')
        self.attachments_dir = os.path.join(datadir, 'attachments')
        self.trash_dir = os.path.join(datadir, 'err')
        print self.logs_dir, self.attachments_dir
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        if not os.path.exists(self.attachments_dir):
            os.makedirs(self.attachments_dir)
        if not os.path.exists(self.attachments_dir):
            os.makedirs(self.trash_dir)

        with open('logger.yaml', 'r') as f:
            conf = yaml.load(f)
            conf['handlers']['info']['filename'] = os.path.join(self.logs_dir, 'import.log')
            conf['handlers']['error']['filename'] = os.path.join(self.logs_dir, 'error.log')
        logging.config.dictConfig(conf)
        self.logging = logging.getLogger('info')
        self.error = logging.getLogger('error')

    def w2n_check_and_commit(self):
        self.count += 1
        if self.count >= 100:
            self.tx.commit()
            self.tx = self.graph.begin()
            self.count = 0
        else:
            self.tx.process()

    def w2n_EmailAddress_SENT_Message(self, email, message_id):
        self.tx.run("MERGE (user:EmailAddress {name: {email_address}, display_name: {email_name}}) "
                    "MERGE (email: Message {message_id: {message_id}}) "
                    "MERGE (user)-[:SENT]->(email)",
                    email_address=email['address'],
                    email_name=email['name'],
                    message_id=message_id)
        self.w2n_check_and_commit()

    def w2n_Message_TO_EmailAddress(self, message_id, email):
        self.tx.run("MERGE (email: Message {message_id: {message_id}}) "
                    "MERGE (user:EmailAddress {name: {email_address}, display_name: {email_name}}) "
                    "MERGE (email)-[:TO]->(user)",
                    message_id=message_id,
                    email_address=email['address'],
                    email_name=email['name'])
        self.w2n_check_and_commit()

    def w2n_Message_CC_EmailAddress(self, message_id, email):
        self.tx.run("MERGE (email: Message {message_id: {message_id}}) "
                    "MERGE (user:EmailAddress {name: {email_address}, display_name: {email_name}}) "
                    "MERGE (email)-[:CC]->(user)",
                    message_id=message_id,
                    email_address=email['address'],
                    email_name=email['name'])
        self.w2n_check_and_commit()

    def w2n_Message_CONTAINS_Url(self, message_id, url):
        self.tx.run("MERGE (email: Message {message_id: {message_id}}) "
                    "MERGE (url: Url {full_link: {url_full}, scheme: {scheme}, sub_domain: {sub}, domain: {domain}, document: {document} }) "
                    "MERGE (email)-[:CONTAINS]->(url)",
                    message_id=message_id,
                    url_full=url['full'],
                    scheme=url['scheme'],
                    sub=url['sub_domain'],
                    domain=url['domain'],
                    document=url['document'])
        self.w2n_check_and_commit()

    def w2n_Url_BELONGS_TO_Domain(self, url, domain):
        self.tx.run("MERGE (url: Url {full_link: {url_full}, scheme: {scheme}, sub_domain: {sub}, domain: {domain}, document: {document} }) "
                    "MERGE (domain: Domain {name: {original_domain}}) "
                    "MERGE (url)-[:BELONGS_TO]->(domain)",
                    url_full=url['full'],
                    scheme=url['scheme'],
                    sub=url['sub_domain'],
                    domain=url['domain'],
                    document=url['document'],
                    original_domain=domain)
        self.w2n_check_and_commit()

    def w2n_EmailAddress_BELONGS_TO_Domain(self, email, domain):
        self.tx.run("MERGE (user:EmailAddress {name: {email_address}, display_name: {email_name}}) "
                    "MERGE (domain: Domain {name: {original_domain}}) "
                    "MERGE (user)-[:BELONGS_TO]->(domain)",
                    email_address=email['address'],
                    email_name=email['name'],
                    original_domain=domain)
        self.w2n_check_and_commit()

    def w2n_Url_POSTED_BY_EmailAddress(self, url, email):
        self.tx.run("MERGE (user:EmailAddress {name: {email_address}, display_name: {email_name}}) "
                    "MERGE (url: Url {full_link: {url_full}, scheme: {scheme}, sub_domain: {sub}, domain: {domain}, document: {document} }) "
                    "MERGE (url)-[:POSTED_BY]->(user)",
                    url_full=url['full'],
                    scheme=url['scheme'],
                    sub=url['sub_domain'],
                    domain=url['domain'],
                    document=url['document'],
                    email_address=email['address'],
                    email_name=email['name'])
        self.w2n_check_and_commit()

    def w2n_Message_HAS_Header(self, message_id, headers):
        data = []
        for key in headers.keys():
            value = u"{0}".format(headers.get(key))
            data.append(u' {0}: \'{1}\''.format(
                key.replace('-', '_'), value.replace("'", '"')))

        self.tx.run(u"MERGE (email:Message {{message_id: {{message_id}}}}) "
                    "MERGE (header:Header {{{0}}}) "
                    "MERGE (email)-[:HAS]->(header)".format(','.join(data)),
                    message_id=message_id)
        self.w2n_check_and_commit()

    def w2n_Part_HAS_Header(self, part_id, headers):
        data = []
        for key in headers.keys():
            value = u"{0}".format(headers.get(key))
            data.append(u' {0}: \'{1}\''.format(
                key.replace('-', '_'), value.replace("'", '"')))

        self.tx.run(u"MERGE (part:MessagePart {{part_id: {{part_id}}}}) "
                    "MERGE (header:Header {{{0}}}) "
                    "MERGE (part)-[:HAS]->(header)".format(','.join(data)),
                    part_id=part_id)
        self.w2n_check_and_commit()

    def w2n_Part_HAS_Part(self, parent_part_id, childrent_part_ids):
        for child_part_id in childrent_part_ids:
            self.tx.run("MERGE (p_part:MessagePart {parent_part_id: {parent_part_id}}) "
                         "MERGE (part:MessagePart {child_part_id: {child_part_id}}) "
                         "MERGE (p_part)-[:HAS]->[part]",
                         parent_part_id=parent_part_id,
                         child_part_id=child_part_id)
            self.w2n_check_and_commit()

    def w2n_Message_HAS_Part(self, message_id, part_id):
        self.tx.run("MERGE (email:Message {message_id: {message_id}}) "
                    "MERGE (part:MessagePart {part_id: {part_id}}) "
                    "MERGE (email)-[:HAS]->(part)",
                    message_id=message_id,
                    part_id=part_id)
        self.w2n_check_and_commit()

    # def w2n_

    @staticmethod
    def extract_url_from_text_plain(string):
        regex = r'('
        regex += r'(?:(https?|s?ftp):\/\/)?'
        regex += r'(?:www\.)?'
        regex += r'('
        regex += r'(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)'
        regex += r'([A-Z]{2,6})'
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

    @staticmethod
    def parse_email_date(dateStr):
        # convert all time to UTC +0000
        date = datetime.datetime.fromtimestamp(
            time.mktime(email.utils.parsedate(dateStr[:-6])))
        offsetDir = dateStr[-5]
        offsetHours = int(dateStr[-4:-2])
        offsetMins = int(dateStr[-2:])
        if offsetDir == "-":
            offsetHours = -offsetHours
            offsetMins = -offsetMins
        return date + datetime.timedelta(hours=offsetHours, minutes=offsetMins)

    def __url01_process_mime_part(self, part):
        result = set()
        if part.body:
            if part.content_type.main == 'text':
                if part.content_type.sub == 'plain':
                    for line in part.body.splitlines():
                        data, _, _, _, _, _ = self.extract_url_from_text_plain(
                            line)
                        if data and validators.url(data):
                            result.add(data)
                if part.content_type.sub == 'html':
                    tmp = self.extract_url_from_text_html(
                        part.body.replace('\n', ''))
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
        self.w2n_EmailAddress_SENT_Message(self.sender, self.message_id)
        self.w2n_EmailAddress_BELONGS_TO_Domain(
            self.sender, self.sender['address'].split('@')[-1])
        for to_email in self.receivers['to']:
            self.w2n_Message_TO_EmailAddress(self.message_id, to_email)
            self.w2n_EmailAddress_BELONGS_TO_Domain(
                to_email, to_email['address'].split('@')[-1])
        for cc_email in self.receivers['cc']:
            self.w2n_Message_CC_EmailAddress(self.message_id, cc_email)
            self.w2n_EmailAddress_BELONGS_TO_Domain(
                cc_email, cc_email['address'].split('@')[-1])

    def url01(self, msg):
        # mappings of URL in headers or message bodies

        result = self.__url01_process_mime_part(msg)
        for data in result:
            _, scheme, full_domain, _, _, document = self.extract_url_from_text_plain(
                data)
            tmp = tldextract.extract(full_domain)
            url = {
                'full': str(data),
                'scheme': str(scheme),
                'sub_domain': tmp.subdomain,
                'domain': '.'.join(tmp[1:]),
                'document': str(document)
            }
            self.w2n_Message_CONTAINS_Url(self.message_id, url)
            self.w2n_Url_BELONGS_TO_Domain(url, url['domain'])
            self.w2n_Url_POSTED_BY_EmailAddress(url, self.sender)

    def headers(self, msg):
        self.w2n_Message_HAS_Header(self.message_id, msg.headers)
        if msg.parts:
            stack = []
            num = []
            for part in msg.walk():
                if stack:
                    upper_id = stack.pop()
                    count = num.pop()
                else:
                    upper_id = msg.message_id
                    count = 0

                part_id = upper_id + '-{0}'.format(count)

                if part.detected_content_type.value.startswith('multipart'):
                    for j in range(len(part.parts)):
                        stack.append(part_id)
                        num.append(j)
                self.w2n_Message_HAS_Part(upper_id, part_id)
                self.w2n_Part_HAS_Header(part_id, part.headers)

    def attachments(self, msg):
        for part in msg.walk(with_self=True):
            if part.is_attachment():
                # 20150821132259_polfilm@gmail.com_<flanker-msg-guid>_<original-filename>.ext
                d = self.parse_email_date(msg.headers['Date'])
                filename = '{0}_{1}_{2}_{3}'.format(
                    d.strftime("%Y%m%d%H%M%S"),
                    self.sender['address'],
                    msg.message_id,
                    part.detected_file_name)
                filepath = os.path.join(self.attachments_dir, d.strftime("%Y%m"))
                if not os.path.exists(filepath):
                    os.makedirs(filepath)

                with open(filepath + filename, 'wb') as f:
                    f.write(part.body)

    def ip01(self, msg):
        ip_found = re.findall(
            r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', msg.to_string())
        pass

    def process(self, msg):
        # count how many time connect to neo4j
        self.count = 0
        # initialize message basic information
        self.message_id = str(msg.message_id)

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

        for value in address.parse_list(msg.headers.get('Cc')):
            tmp = {
                'address': value.address,
                'name': value.display_name
            }
            self.receivers['cc'].append(tmp)

        self.tx = self.graph.begin()

        for func in self.processors:
            getattr(self, func)(msg)

        # commit remainder
        self.tx.commit()

