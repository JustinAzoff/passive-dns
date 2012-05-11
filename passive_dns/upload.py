#!/usr/bin/env python
"""Iterate through a directory of dns pcap files and
export any new and unchanging file to plain txt"""

import os
import time
import datetime
from passive_dns import client
from passive_dns import config
from passive_dns.common import next_filename, is_growing

LOC = config.read_config()['DATADIR']

def upload(fn):
    c = client.SearchClient()
    r = c.upload_pcap(fn)
    r.raise_for_status()
    os.unlink(fn)
    return r.text

def main():
    for f in os.listdir(LOC):
        f = os.path.join(LOC, f)
        if not os.path.exists(f): #file disappeared
            continue
        if '.pcap' not in f:
            continue

        if os.path.exists(next_filename(f)) or not is_growing(f):
            print 'upload', f
            print upload(f)

if __name__ == "__main__":
    main()
