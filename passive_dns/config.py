import os

def _read_config(fn):
    config = {}
    execfile(fn,{},config)
    return config

def read_config():
    home = os.path.expanduser("~/.passive_dns.cfg")
    system = "/etc/passivedns.cfg"
    cur = "passive_dns.cfg"

    configs = (cur, home, system)
    for fn in configs:
        if os.path.exists(fn):
            return _read_config(fn)

    raise Exception("No configuration file found (tried %s, %s and %s) " % configs)
