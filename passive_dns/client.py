import xmlrpclib
from simplejson import loads as load_json


class SearchClient:
    def __init__(self, server="http://joe:7084"):
        self.s = xmlrpclib.Server(server)

    def search_answer(self, q):
        return load_json(self.s.search_answer(q))

    def search_question(self, q):
        return load_json(self.s.search_question(q))

    def reopen_files(self):
        return self.s.reopen_files()

def show(r):
    print "%(key)s %(value)s %(type)s %(ttl)s %(first)s %(last)s" % r

def main():
    import sys
    q = sys.argv[1]
    s = SearchClient()
    for x in s.search_question(q):
        show(x)

    for x in s.search_answer(q):
        show(x)

if __name__ == "__main__":
    main()
