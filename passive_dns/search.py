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
        self.map.readline()
        return self.map.tell()

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
        pos = 0
        start = 0
        end = self.size
        found = False
        while start < end:
            mid = start + (end-start)/2
            self.map.seek(mid)
            pos = self.find_newline()
            if pos > end:
                break
            line = self.map.readline()
            if q < line:
                end = mid
            elif q > line:
                start = mid



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
