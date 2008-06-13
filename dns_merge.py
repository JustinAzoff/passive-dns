#!/usr/bin/env python
import os
import sys

from dns_common import make_hash

def merge(files):
    #TODO: use heapq instead of min?
    files = dict([(f,None) for f in files])

    #load in the first key, value from each file
    for f in files.keys():
        try :
            line = f.next() 
            files[f] = line, f
        except StopIteration:
            del files[f]

    while files:
        line, f = min(files.values())
        yield line

        try :
            line = f.next()
            files[f] = line, f
        except StopIteration:
            del files[f]


def merge_sorted(sorted_stream, output):
    if os.path.exists(output) and output!="/dev/stdout":
        raise Exception("Output file %s already exists" % output)
    f = open(output,'w')
    sorted_stream = iter(sorted_stream)

    try:
        line = sorted_stream.next()
    except StopIteration:
        return
    prev = cur = make_hash(line)

    for line in sorted_stream:
        cur = make_hash(line)

        #should have just left it as a list so if cur[0:3] == prev[0:3]
        if (cur['key']  ==prev['key'] and
            cur['value']==prev['value'] and
            cur['type'] ==prev['type']):
            prev['first'] = min(prev['first'], cur['first'])
            prev['last']  = max(prev['last'],  cur['last'])
        else:
            f.write("%(key)s %(value)s %(type)s %(ttl)s %(first)s %(last)s\n" % prev)
            prev = cur

    if cur:
        f.write("%(key)s %(value)s %(type)s %(ttl)s %(first)s %(last)s\n" % cur)

def do_merge(streams, output):
    merged = merge(streams)
    merge_sorted(merged, output)

if __name__ == "__main__":
    output = sys.argv[1]
    fns = sys.argv[2:]
    fps = [open(f) for f in fns]
    do_merge(fps, output)
