import requests
try :
    from json import loads as load_json
except ImportError:
    from simplejson import loads as load_json
from passive_dns import config
from passive_dns.common import calc_checksum

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

    def upload_pcap(self, filename):
        with open(filename, 'rb') as f:
            body = f.read()

        checksum = calc_checksum(body)
        data  = { "checksum": checksum}
        files = { "upload.pcap": ("upload.pcap", body)}
        return requests.post(self.server + "/upload_pcap", files=files, data=data)

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
