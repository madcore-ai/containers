class Domain_EmailAddresses():

    def __init__(self, conn, domain):
        self.conn = conn
        self.domain = domain

    @property
    def query_string(self):
        return ('MATCH (e:EmailAddress)-[:BELONGS_TO]->(d:Domain) '
                'WHERE d.name = "{0}" '
                'RETURN e.display_name as name, e.name as email'.format(self.domain))

    def __query(self):
        return self.conn.data(self.query_string)

    def get_result(self):
        return self.__query()
