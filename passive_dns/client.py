import xmlrpclib
import simplejson


class SearchClient:
    def __init__(self, server="http://joe:7084"):
        self.s = xmlrpclib.Server(server)

    def search_answer(self, q):
        return simplejson.loads(self.s.search_answer(q))

    def search_question(self, q):
        return simplejson.loads(self.s.search_question(q))

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
