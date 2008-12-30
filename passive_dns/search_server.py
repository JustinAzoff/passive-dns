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
from passive_dns.common import query_dir, answer_dir

import simplejson

class SearchServer(xmlrpc.XMLRPC):
    def __init__(self):
        self.q_search = self.a_search = None
        LoopingCall(self._reopen).start(300)

    def _reopen(self):
        print "reopening data files"
        self.q_search and self.q_search.close()
        self.a_search and self.a_search.close()

        self.q_search = dns_search.SearcherMany(glob.glob(os.path.join(query_dir,  "dns_*")))
        self.a_search = dns_search.SearcherMany(glob.glob(os.path.join(answer_dir, "dns_*")))
    
    def xmlrpc_hello(self):
        return 'hello'

    def xmlrpc_search_question(self, q):
        return simplejson.dumps(list(self.q_search.search(query=q)))

    def xmlrpc_search_answer(self, q):
        return simplejson.dumps(list(self.a_search.search(answer=q)))

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
    i = internet.TCPServer(7084, site)
    i.setServiceParent(serviceCollection)

    #i = internet.SSLServer(7083, site, ServerContextFactory())
    #i.setServiceParent(serviceCollection)

    i.startService()
    reactor.run()

if __name__ == "__main__": 
    main()
