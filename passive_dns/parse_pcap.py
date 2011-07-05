#!/usr/bin/env python
"""Extract from a pcap file of all dns queries:
time, query, answer, type, ttl
"""
import time, datetime
from scapy.all import sniff, IP, DNS, DNSQR, DNSRR

def date(d):
    return datetime.datetime.fromtimestamp(d).strftime("%Y-%m-%d %H:%M:%S")

def payloads(x):
    yield x
    while True:
        x = x.payload
        if x:
            yield x
        else:
            break

wanted_types = ['A', 'CNAME']

class Statmaker:
    def __init__(self):
        self.ipnames = {}

    def __call__(self, pkt):
        ipn = self.ipnames
        if DNSRR not in pkt:
            return
        ts = pkt.time
        dnsrr = pkt[DNSRR]
        query = dnsrr.rrname

        resp = [(r.rdata, r.sprintf("%type%"), r.ttl) for r in payloads(dnsrr)]

        for answer, type, ttl in resp:
            tup = (answer, query, type)
            if type not in wanted_types: continue
            if tup in ipn:
                r = ipn[tup]
                r.update({'last': ts, 'ttl': ttl})
            else:
                ipn[tup]={'first': ts, 'last': ts, 'ttl': ttl}

        
def parse(fn):
    """Process a pcap file and return a dictionary of
        (answer, query, type) -> {first, last, ttl}"""
    s = Statmaker()
    sniff(offline=fn, prn=s, store=0)

    return s

def report(fn, answer_outfn, query_outfn):
    s = parse(fn)
    af = open(answer_outfn, 'w')
    qf = open(query_outfn, 'w')

    data = s.ipnames.items()
    data.sort()

    for (answer, query, type), rec in data:
        af.write("%s %s %s %s %s %s\n" % (answer, query, type, rec['ttl'], date(rec['first']),date(rec['last'])))
    af.close()

    #sort by the reversed query string
    data = [((query[::-1], answer, type), rec) for ((answer, query, type), rec) in data]
    data.sort()
    for (rquery, answer, type), rec in data:
        qf.write("%s %s %s %s %s %s\n" % (rquery, answer, type, rec['ttl'], date(rec['first']),date(rec['last'])))
    qf.close()

    return len(data)

if __name__ == "__main__":
    import sys
    inf = sys.argv[1]
    outf = "/dev/stdout"
    if len(sys.argv) > 3:
        outfa = sys.argv[2]
        outfq = sys.argv[3]
    if outf == "auto":
        outfa = inf.replace(".pcap","ans.txt")
        outfq = inf.replace(".pcap","que.txt")
        if outfa == inf:
            raise Exception("Same filename???")
    report(inf, outfa, outfq)
