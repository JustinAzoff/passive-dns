#!/usr/bin/env python
"""Iterate through a directory of dns pcap files and
export any new and unchanging file to plain txt"""

import os
import time
import datetime
from passive_dns import parse_pcap
from passive_dns import client
from passive_dns import config
from passive_dns.common import next_filename, is_growing

LOC = config.read_config()['DATADIR']
answer_dir = os.path.join(LOC, "by_answer")
query_dir  = os.path.join(LOC, "by_query")

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

    work_done = False


    for f in os.listdir(LOC):
        f = os.path.join(LOC, f)
        if not os.path.exists(f): #file disappeared
            continue
        if 'processing' in f or 'pcap' not in f: continue

        if os.path.exists(next_filename(f)) or not is_growing(f):
            process(f)
            work_done = True

    if work_done:
        client.SearchClient().reopen_files()
        

if __name__ == "__main__":
    main()
