class EmailAddress_Outgoing_Urls():

    def __init__(self, conn, email_address):
        self.conn = conn
        self.email_address = email_address

    @property
    def query_string(self):
        return ('MATCH (e:EmailAddress)-[:SENT]->(m:Message), '
                '(m)-[:CONTAINS]->(u:Url) '
                'WHERE e.name = "{0}" '
                'RETURN u.full_link as url'.format(self.email_address))

    def __query(self):
        return self.conn.data(self.query_string)

    def get_result(self):
        return self.__query()
