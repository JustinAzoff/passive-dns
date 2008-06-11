#!/usr/bin/env python
import pcapy
import dns.message
import time, datetime
import psyco
psyco.full()

OFFSET = 42
A = 1

def date(d):
    return datetime.datetime.fromtimestamp(d).strftime("%Y-%m-%d %H:%M:%S")

def get_ips(m):
    for a in m.answer:
        if a.rdtype != A: continue
        for i in a:
            yield i.to_text(), a.ttl

def get_query(m):
    query = m.question[0].to_text().split()[0]
    return query
        
class Statmaker:
    def __init__(self):
        self.ipnames = {}

    def __call__(self, header, data):

        ts, _ =  header.getts()
        try :
            m = dns.message.from_wire(data[OFFSET:])
        except:
            return
        query = get_query(m)

        ipn = self.ipnames

        for ip, ttl in get_ips(m):
            tup = (ip, query)
            if tup in ipn:
                r = ipn[tup]
                r.update({'last': ts, 'ttl': ttl})
            else:
                ipn[tup]={'first': ts, 'last': ts, 'ttl': ttl}

        
def parse(fn):
    s = Statmaker()
    pcap = pcapy.open_offline(fn)
    pcap.loop(0, s)
    for (ip, name), rec in s.ipnames.iteritems():
        print ip, name, rec['ttl'], date(rec['first']),date(rec['last'])

if __name__ == "__main__":
    import sys
    parse(sys.argv[1])
