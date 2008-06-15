#!/usr/bin/env python
"""Iterate through a directory of dns pcap files and
export any new and unchanging file to plain txt"""

import os
import time
import datetime
from passive_dns import parse_pcap

LOC="/var/captures/dns/"

answer_dir = os.path.join(LOC, "by_answer")
query_dir  = os.path.join(LOC, "by_query")

SIZE_TIMEOUT = 5

def next_filename(f):
    if not f[-1].isdigit():
        return f + '1'

    fn, number = f.split(".pcap")
    new_number = int(number) + 1
    return "%s.pcap%d" % ( fn, new_number)

def is_growing(f):
    size = os.stat(f).st_size
    time.sleep(0.1)
    for x in range(SIZE_TIMEOUT):
        time.sleep(1)
        newsize = os.stat(f).st_size
        if newsize != size:
            return True
    return False

def find(d):
    for d, path, files in os.walk(d):
        for f in files:
            fn = os.path.join(d, f)
            yield(fn)

def get_filename_from_pcap(fn):
    pcap_time = datetime.datetime.fromtimestamp(os.stat(fn).st_mtime)
    new_name = pcap_time.strftime("dns_%Y-%m-%d_%H:%M.txt")
    return new_name

def make_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def process(fn):
    print 'process', fn,

    outfn = get_filename_from_pcap(fn)
    answer_outfn = os.path.join(answer_dir, outfn)
    query_outfn = os.path.join(query_dir, outfn)


    newfn = fn + ".processing"
    os.rename(fn, newfn)
    records = parse_pcap.report(newfn, answer_outfn, query_outfn)
    print records
    os.unlink(newfn)


def main():
    for d in answer_dir, query_dir:
        make_dir(d)

    for f in os.listdir(LOC):
        f = os.path.join(LOC, f)
        if 'processing' in f or 'pcap' not in f: continue

        if os.path.exists(next_filename(f)) or not is_growing(f):
            process(f)

if __name__ == "__main__":
    main()
