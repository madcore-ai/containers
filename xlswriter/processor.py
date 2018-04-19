from logger import Logger

class Worker(Logger):

    def __init__(self, conn, *args, **kargs):
        super(self.__class__, self).__init__(self.__class__.__name__)
        self.conn = conn
        self.kargs = kargs

    def build_query(self, query):
        return query.format(**self.kargs)

    def __query(self, query):
        self.logger.info(query)
        return self.conn.data(query)

    def get_result(self, query):
        query = self.build_query(query)
        return self.__query(query)
