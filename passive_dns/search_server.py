#!/usr/bin/env python

import os, glob
from passive_dns import search as dns_search
from passive_dns import config

import tornado.options
import tornado.httpserver
import tornado.ioloop
import tornado.web

import logging

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

        LOC = config.read_config()['DATADIR']
        answer_dir = os.path.join(LOC, "by_answer")
        query_dir  = os.path.join(LOC, "by_query")

        self.q_search = dns_search.SearcherMany(glob.glob(os.path.join(query_dir,  "dns_*")))
        self.a_search = dns_search.SearcherMany(glob.glob(os.path.join(answer_dir, "dns_*")))

#FIXME: This should be passed in from main somehow, yes?
P = PassiveDnsSearcher()

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello\n')

class SearchQuery(tornado.web.RequestHandler):
    def get(self, q):
        self.write(dump_json(list(P.q_search.search(query=q))))

class SearchAnswer(tornado.web.RequestHandler):
    def get(self, q):
        self.write(dump_json(list(P.a_search.search(answer=q))))

class Search(tornado.web.RequestHandler):
    def get(self, q):
        queries = list(P.q_search.search(query=q))
        answers = list(P.a_search.search(answer=q))
        self.write(dump_json(queries + answers))

class Reopen(tornado.web.RequestHandler):
    def post(self):
        P.reopen()
        self.write("ok\n")

def main():
    tornado.options.parse_command_line()

    cfg = config.read_config()
    iface = cfg['SERVER_BIND']
    port  = cfg['SERVER_PORT']

    application = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/search/query/(..*)", SearchQuery),
        (r"/search/answer/(..*)", SearchAnswer),
        (r"/search/(..*)", Search),
        (r"/reopen", Reopen),
        ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port, iface)
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(P.reopen,1000*60*5,io_loop).start()
    io_loop.start()

if __name__ == "__main__": 
    main()
