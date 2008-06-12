#!/usr/bin/env python
import os
import sys

def get_file(fn):
    if fn.endswith(".gz"):
        f = os.popen('zcat "%s"' % fn)
    else:
        f = open(fn)
    for line in f:
        yield line.split()
    f.close()

def parse_file(fn, data):
    for parts in get_file(fn):
        if len(parts)==7:
            answer, query, ttl, datefirst,timefirst, datelast,timelast = parts
            type = 'A'
        elif len(parts)==8:
            answer, query, type, ttl, datefirst,timefirst, datelast,timelast = parts

        first = datefirst + ' ' + timefirst
        last  = datelast  + ' ' + timelast
        rec = data.get((answer,query, type))
        if rec:
            rec['ttl'] = ttl
            rec['first'] = min(first, rec['first'])
            rec['last'] =  max(last,  rec['last'])
        else:
            data[(answer, query, type)] = {'ttl': ttl, 'first': first, 'last': last}


def merge(files):
    data = {}
    for f in files:
        parse_file(f, data)

    data = data.items()
    data.sort()
    for (answer,query, type), rec in data:
        print answer, query, type, rec['ttl'], rec['first'], rec['last']

if __name__ == "__main__":
    fns = sys.argv[1:]
    if not fns:
        fns=['/dev/stdin']
    merge(fns)
