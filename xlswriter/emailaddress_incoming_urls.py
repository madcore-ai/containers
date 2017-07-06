from logger import Logger


class EmailAddress_Incomming_Urls(Logger):

    def __init__(self, conn, email_address):
        super(self.__class__, self).__init__(self.__class__.__name__)
        self.conn = conn
        self.email_address = email_address

    @property
    def query_string(self):
        return ('MATCH (m:Message)-[:TO]->(e:EmailAddress), '
                '(m)-[:CONTAINS]->(u:Url) '
                'WHERE e.name = "{0}" '
                'RETURN u.full_link as url'.format(self.email_address))

    def __query(self):
        self.logger.info(self.query_string)
        return self.conn.data(self.query_string)

    def get_result(self):
        return self.__query()
