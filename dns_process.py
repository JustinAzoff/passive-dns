#!/usr/bin/env python
import os
import time
import datetime

LOC="/var/captures/dns/"
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
    new_dir = pcap_time.strftime("%Y/%m/%d")
    new_name = pcap_time.strftime("dns_%Y-%m-%d_%H:%M.txt.gz")

    os.makedirs(os.path.join(LOC, new_dir))
    outfn = os.path.join(LOC, new_dir, new_name)
    return outfn

def process(fn):
    print 'process', fn

    outfn = get_filename_from_pcap(fn)

    newfn = fn + ".processing"
    os.rename(fn, newfn)
    #not sure about leaks, so lets just exec this
    ret = os.system("dns_parse_pcap.py %s %s" % (newfn, outfn))
    if ret != 0:
        raise Exception("Error running dns_parse_pcap %s" % newfn)
    os.unlink(newfn)


def main():
    for f in os.listdir(LOC):
        f = os.path.join(LOC, f)
        if 'processing' in f or 'pcap' not in f: continue

        if os.path.exists(next_filename(f)) or not is_growing(f):
            process(f)

if __name__ == "__main__":
    main()
