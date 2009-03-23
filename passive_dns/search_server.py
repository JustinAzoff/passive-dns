#!/usr/bin/env python

import xmlrpclib
from twisted.web import xmlrpc, server, http, resource
from twisted.internet import defer, protocol, reactor

from twisted.application import service, internet
from twisted.internet.task import LoopingCall

#from OpenSSL import SSL

#import datetime
#import time

import os, glob
from passive_dns import search as dns_search
from passive_dns import config

from simplejson import dumps as dump_json

class SearchServer(xmlrpc.XMLRPC):
    def __init__(self):
        self.q_search = self.a_search = None
        LoopingCall(self._reopen).start(300)

    def _reopen(self):
        print "reopening data files"
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
    
    def xmlrpc_hello(self):
        return 'hello'

    def xmlrpc_search_question(self, q):
        return dump_json(list(self.q_search.search(query=q)))

    def xmlrpc_search_answer(self, q):
        return dump_json(list(self.a_search.search(answer=q)))

    def xmlrpc_reopen_files(self):
        self._reopen()
        return "ok"

class ServerContextFactory:

    def getContext(self):
        """Create an SSL context.

        This is a sample implementation that loads a certificate from a file
        called 'server.pem'."""                               
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_certificate_file('server.pem')
        ctx.use_privatekey_file ('server.pem')
        return ctx

def main():
    application = service.Application('dns_search')
    serviceCollection = service.IServiceCollection(application)
    site = server.Site(resource.IResource(SearchServer()))
    cfg = config.read_config()
    iface = cfg['SERVER_BIND']
    port  = cfg['SERVER_PORT']
    i = internet.TCPServer(port, site, interface=iface)
    i.setServiceParent(serviceCollection)

    #i = internet.SSLServer(7083, site, ServerContextFactory())
    #i.setServiceParent(serviceCollection)

    i.startService()
    reactor.run()

if __name__ == "__main__": 
    main()
