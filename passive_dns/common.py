import os
import time
import hashlib

def make_hash(line):
    parts = line.split()
    if len(parts)==8:
        key, value, type, ttl, datefirst,timefirst, datelast,timelast = parts
    else:
        type = 'A'
        key, value, ttl, datefirst,timefirst, datelast,timelast = parts

    first = datefirst + ' ' + timefirst
    last  = datelast  + ' ' + timelast

    #temp
    value = value.lower()
    key = key.lower()
    if value.endswith("."):
        value=value[:-1]

    return  {'key': key, 'value': value, 'type': type, 'ttl': ttl, 'first': first, 'last': last}

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

def calc_checksum(data):
    checksum = hashlib.md5(data).hexdigest()
    return checksum
