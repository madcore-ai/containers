from logger import Logger


class Domain_Urls(Logger):

    def __init__(self, conn, domain):
        super(self.__class__, self).__init__(self.__class__.__name__)
        self.conn = conn
        self.domain = domain

    @property
    def query_string(self):
        return ('MATCH (u:Url)-[:BELONGS_TO]->(d:Domain) '
                'WHERE d.name = "{0}" '
                'RETURN u.full_link as url'.format(self.domain))

    def __query(self):
        self.logger.info(self.query_string)
        return self.conn.data(self.query_string)

    def get_result(self):
        return self.__query()
