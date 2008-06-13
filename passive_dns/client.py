import xmlrpclib

class SearchClient:
    def __init__(self, server="http://joe:7084"):
        self.s = xmlrpclib.Server(server)

    def search_answer(self, q):
        return self.s.search_answer(q)

    def search_question(self, q):
        return self.s.search_question(q)
