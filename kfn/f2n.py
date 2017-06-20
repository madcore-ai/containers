from neo4j.v1 import GraphDatabase
import re
import validators


def extract_url_from_string(string):
    regex = r'('

    # Scheme (HTTP, HTTPS, FTP and SFTP):
    regex += r'(?:(https?|s?ftp):\/\/)?'

    # www:
    regex += r'(?:www\.)?'

    regex += r'('

    # Host and domain (including ccSLD):
    regex += r'(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\.)+)'

    # TLD:
    regex += r'([A-Z0-9][A-Z0-9-]{0,61}\.[A-Z]{2,6})'

    # IP Address:
    regex += r'|(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

    regex += r')'

    # Port:
    regex += r'(?::(\d{1,5}))?'

    # Query path:
    regex += r'(?:(\/\S+)*)'

    regex += r')'

    find_urls_in_string = re.compile(regex, re.IGNORECASE)
    url = find_urls_in_string.search(string)

    if url is not None and url.group(0) is not None:
        # print("URL parts: " + str(url.groups()))
        # print("URL " + url.group(0).strip())
        return url.group(0).strip(), url.groups()
    return None, None


def w2n_EmailAdress_SENT_Message(tx, email_address, message):
    tx.run("MERGE (user:EmailAddress {name: $email_address}) "
           "MERGE (email: Message {id: $message_id, content: $message_content}) "
           "MERGE (user)-[:SENT]->(email)",
           email_address=email_address,
           message_id=message['id'],
           message_content=message['content'])


def w2n_Message_TO_EmailAdress(tx, message, email_address):
    pass


def w2n_Message_CC_EmailAdress(tx, message, email_address):
    pass


def w2n_Message_CONTAINS_Url(tx, message, url):
    tx.run("MERGE (email: Message {id: $message_id, content: $message_content}) "
           "MERGE (url: Url {full_link: $url_full, scheme: $scheme, sub_domain: $sub, domain: $domain, document: $document }) "
           "MERGE (email)-[:CONTAINS]->(url)",
           message_id=message['id'],
           message_content='fakecontent',
           url_full=url['full'],
           scheme=url['scheme'],
           sub='wwww',
           domain=url['domain'],
           document=url['document'])


def w2n_Url_BELONGS_TO_Domain(tx, url, domain):
    pass


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

    def __url01_process_mime_part(self, part):
        result = set()
        if part.body:
            # main process , extract url
            for line in part.body.splitlines():
                data, _ = extract_url_from_string(line)
                if data:
                    result.add(data)
        else:
            for p in part.parts:
                data_list = self.__url01_process_mime_part(p)
                if data_list:
                    result.union(data_list)

        # print result
        return result

    def url01(self, msg):
        # mappings of URL in headers or message bodies
        message = {
            'id': str(msg.message_id),
            'content': msg.to_string()
        }

        result = self.__url01_process_mime_part(msg)
        for data in result:
            if validators.url(data):
                _, tmp = extract_url_from_string(data)
                _, scheme, full_domain, domain, _, document = tmp
                url = {
                    'full': str(data),
                    'scheme': str(scheme),
                    'domain': str(domain),
                    'document': str(document)
                }
                with self.driver.session() as session:
                    session.write_transaction(
                        w2n_Message_CONTAINS_Url, message, url)

    def ip01(self, msg):
        ip_found = re.findall(
            r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', msg.to_string())
        pass

    def process(self, msg):
        for func in self.processors:
            getattr(self, func)(msg)
