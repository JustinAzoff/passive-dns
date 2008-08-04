#!/usr/bin/env python
"""Merge multiple dns txt files together.
Also used to merge search results from individual txt files"""

import os
import sys
import datetime

from passive_dns.common import make_hash

#like sort -m
def merge(files):
    """Merge mutliple sorted files(or any iterable) together"""
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


def merge_sorted(sorted_stream):
    """Merge consecutive dns records together"""
    #TODO: use itertools.groupby?
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
            prev['first'] = cur['first'] = min(prev['first'], cur['first'])
            prev['last']  = cur['last']  = max(prev['last'],  cur['last'])
        else:
            yield prev
            prev = cur

    if cur:
        yield cur

def merge_and_merge(streams):
    merged = merge(streams)
    return merge_sorted(merged)

def do_merge_to_file(streams, output):
    if os.path.exists(output) and output!="/dev/stdout":
        raise Exception("Output file %s already exists" % output)
    f = open(output,'w')

    week_ago = str(datetime.datetime.today() - datetime.timedelta(days=7))
    for cur in merge_and_merge(streams):
        if cur['last'] <= week_ago: continue
        f.write("%(key)s %(value)s %(type)s %(ttl)s %(first)s %(last)s\n" % cur)

def main():
    output = sys.argv[1]
    fns = sys.argv[2:]
    fps = [open(f) for f in fns]
    do_merge_to_file(fps, output)

if __name__ == "__main__":
    main()
