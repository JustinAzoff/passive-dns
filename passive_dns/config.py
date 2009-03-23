import os

def _read_config(fn):
    config = {}
    execfile(fn,{},config)
    return config

def find_config():
    home = os.path.expanduser("~/.passive_dns.cfg")
    system = "/etc/passive_dns.cfg"
    cur = "passive_dns.cfg"

    configs = (cur, home, system)
    for fn in configs:
        if os.path.exists(fn):
            return fn

    raise Exception("No configuration file found (tried %s, %s and %s) " % configs)

def read_config():
    fn = find_config()
    return _read_config(fn)

def dump_config():
    fn = find_config()
    print open(fn).read()
