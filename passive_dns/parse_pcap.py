#!/usr/bin/env python
"""Extract from a pcap file of all dns queries:
time, query, answer, type, ttl
"""
import pcapy
import dns.message
import time, datetime
import gzip
try:
    import psyco
    psyco.full()
except:
    pass

OFFSET = 42
A = 1
AAAA = 28
CNAME = 5

TYPES = {
    A: 'A',
    AAAA: 'AAAA',
    CNAME: 'CNAME'
}

def date(d):
    return datetime.datetime.fromtimestamp(d).strftime("%Y-%m-%d %H:%M:%S")

def get_answers(m):
    for a in m.answer:
        if a.rdtype not in TYPES: continue
        for i in a:
            yield i.to_text().lower(), TYPES[a.rdtype], a.ttl
#            if a.rdtype == CNAME:
                #raise 'test'

def get_query(m):
    try :
        query = m.question[0].to_text().split()[0]
    except IndexError:
        return None
    if query.endswith("."):
        query = query[:-1]
    return query.lower()
        
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
        if not query:
            return

        ipn = self.ipnames

        for answer, type, ttl in get_answers(m):
            tup = (answer, query, type)
            if tup in ipn:
                r = ipn[tup]
                r.update({'last': ts, 'ttl': ttl})
            else:
                ipn[tup]={'first': ts, 'last': ts, 'ttl': ttl}

        
def parse(fn):
    """Process a pcap file and return a dictionary of
        (answer, query, type) -> {first, last, ttl}"""
    s = Statmaker()
    pcap = pcapy.open_offline(fn)
    pcap.loop(0, s)

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
