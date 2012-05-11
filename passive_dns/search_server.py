#!/usr/bin/env python

import os, glob
import time
from passive_dns import search as dns_search
from passive_dns import config

import tornado.options
import tornado.httpserver
import tornado.ioloop
import tornado.web

import logging

import urllib2

from passive_dns.common import calc_checksum

cfg = config.read_config()
DATADIR = cfg['DATADIR']
UPLOADERS = set(cfg.get('UPLOADERS','').split(","))

try :
    from json import dumps as dump_json
except ImportError:
    from simplejson import dumps as dump_json

class PassiveDnsSearcher:

    def __init__(self):
        self.q_search = self.a_search = None
        self.reopen()

    def reopen(self):
        logging.debug("reopening data files")
        try :
            self.q_search and self.q_search.close()
        except:
            pass

        try :
            self.a_search and self.a_search.close()
        except:
            pass

        answer_dir = os.path.join(DATADIR, "by_answer")
        query_dir  = os.path.join(DATADIR, "by_query")

        self.q_search = dns_search.SearcherMany(glob.glob(os.path.join(query_dir,  "dns_*")))
        self.a_search = dns_search.SearcherMany(glob.glob(os.path.join(answer_dir, "dns_*")))

#FIXME: This should be passed in from main somehow, yes?
P = PassiveDnsSearcher()

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello\n')

class SearchQuery(tornado.web.RequestHandler):
    def get(self, q):
        q = urllib2.unquote(q)
        self.write(dump_json(list(P.q_search.search(query=q))))

class SearchAnswer(tornado.web.RequestHandler):
    def get(self, q):
        q = urllib2.unquote(q)
        self.write(dump_json(list(P.a_search.search(answer=q))))

class Search(tornado.web.RequestHandler):
    def get(self, q):
        q = urllib2.unquote(q)
        queries = list(P.q_search.search(query=q))
        answers = list(P.a_search.search(answer=q))
        self.write(dump_json(queries + answers))

class Reopen(tornado.web.RequestHandler):
    def post(self):
        P.reopen()
        self.write("ok\n")

class UploadPcap(tornado.web.RequestHandler):
    def post(self):
        remote_ip = self.request.remote_ip
        if remote_ip not in UPLOADERS:
            raise tornado.web.HTTPError(403)
        body = self.request.files['upload.pcap'][0]['body']
        expected_checksum = self.request.get_argument("checksum")

        checksum = calc_checksum(body)
        if checksum != expected_checksum:
            raise tornado.web.HTTPError(500, "checksum mismatch")

        out = "dns_%s_%s.pcap" % (remote_ip, time.time())
        with open(os.path.join(DATADIR, out), 'wb') as f:
            f.write(body)
        return self.write("ok")

def main():
    tornado.options.parse_command_line()

    iface = cfg['SERVER_BIND']
    port  = cfg['SERVER_PORT']

    application = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/search/query/(..*)", SearchQuery),
        (r"/search/answer/(..*)", SearchAnswer),
        (r"/search/(..*)", Search),
        (r"/reopen", Reopen),
        (r"/upload_pcap", UploadPcap),
        ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port, iface)
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(P.reopen,1000*60*5,io_loop).start()
    io_loop.start()

if __name__ == "__main__": 
    main()
