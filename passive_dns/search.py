#!/usr/bin/env python
import sys
import os
import mmap

from passive_dns import merge

def do_mmap(f):
    fd = os.open(f, os.O_RDONLY)
    size = os.lseek(fd, 0, 2)
    os.lseek(fd, 0, 0)
    m = mmap.mmap(fd, size, prot=mmap.PROT_READ)
    return m, size, fd

SEEK_SET = 0
SEEK_CUR = 1

class Searcher:
    def __init__(self, file):
        self.file = file
        self.map, self.size, self.fd = do_mmap(file)

    def close(self):
        self.map.close()
        os.close(self.fd)

    def find_newline(self):
        cur = self.map.tell()
        seek_to = max(0, cur - 200)
        self.map.seek(seek_to, SEEK_SET)
        data = self.map.read(200)
        last_newline = data.rindex("\n")
        self.map.seek(last_newline - 200 + 1, SEEK_CUR)

    def search(self, q):
        while True:
            line = self.map.readline()
            if q in line:
                sys.stdout.write(line)
            else:
                pos = self.map.find(q)
                if  pos ==-1: break
                self.map.seek(pos)
                self.find_newline()

    def binary_search(self, q):
        start = 0
        end = self.size
        while end - start > 10:
            mid = (start+end)/2
            self.map.seek(mid)
            self.find_newline()
            line = self.map.readline()
            key = line.split(None,2)[0]
            if q < key:
                end = mid
                continue
            elif q > key:
                start = mid
                continue
            else: #found
                break

        mid = (start+end)/2
        self.map.seek(mid)

        #sanity check, is this key even found
        #if I don't do this, self.map.find will search to
        #the end of the file
        self.map.seek(-1024, SEEK_CUR)
        data = self.map.read(1024)
        if q not in data:
            return

        #now, try and find the FIRST occurance of this key
        while True:
            seek_to = max(0, self.map.tell() - 2000)
            self.map.seek(seek_to, SEEK_SET)
            if seek_to == 0:
                break
            pos = self.map.find("\n" + q)
            self.map.seek(pos+1)
            #if I needed to skip back forward more than 1000, I should be OK
            #otherwise jump backwards another 2000 and try again
            if pos - seek_to > 1000:
                break

        while True:
            line = self.map.readline()
            if not line.startswith(q): break
            yield line

class SearcherMany:
    def __init__(self, files):
        self.searchers = [Searcher(f) for f in files]

    def close(self):
        for x in self.searchers:
            x.close()

    def _search(self, q):
        results = [s.binary_search(q) for s in self.searchers]
        merged = merge.merge_and_merge(results)
        return merged

    def search(self, answer=None, query=None):
        if answer:
            q = answer
        if query:
            q = query[::-1]

        results = self._search(q)
        if answer:
            for r in results:
                yield r
        if query:
            for r in results:
                r['key']=r['key'][::-1]
                yield r
    

def main():
    q = sys.argv[1]
    files = sys.argv[2:]
    s = SearcherMany(files)
    for x in s.search(q):
        print "%(key)s %(value)s %(type)s %(ttl)s %(first)s %(last)s" % x


if __name__ == "__main__":
    main()
