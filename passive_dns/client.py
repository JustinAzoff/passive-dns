import requests
try :
    from json import loads as load_json
except ImportError:
    from simplejson import loads as load_json
from passive_dns import config

class SearchClient:
    def __init__(self, server=None):
        if not server:
            server = config.read_config()['SERVER']
        self.server = server

    def _do_search(self, url):
        return load_json(requests.get(self.server + url).content)

    def search(self, q):
        return self._do_search("/search/" + q)

    def search_answer(self, q):
        return self._do_search("/search/answer/" + q)

    def search_question(self, q):
        return self._do_search("/search/query/" + q)

    def reopen_files(self):
        return requests.post(self.server + "/reopen").content

def show(r):
    print "%(key)s %(value)s %(type)s %(ttl)s %(first)s %(last)s" % r

def main():
    import sys
    q = sys.argv[1]
    s = SearchClient()
    for x in s.search(q):
        show(x)

if __name__ == "__main__":
    main()
