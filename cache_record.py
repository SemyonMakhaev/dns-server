#!/usr/bin/env python3
"""A tool for DNS-server realization."""
from struct import pack, unpack
from time import time


DEFAULT_TTL = 900


class CacheRecord:
    """A record in DNS-servers cache representation."""
    def __init__(self, data):
        self.data = data
        self.record_time = time()
        self.ttl = self.get_package_ttl()


    def __eq__(self, obj):
        if not isinstance(obj, CacheRecord):
            return False
        return self.data == obj.data


    def __hash__(self):
        return hash(self.data)


    def __repr__(self):
        return get_name(self.data[12:]).decode()


    def get_package_ttl(self):
        """Returns a ttl of received package."""
        ttl_idx = len(get_name(self.data[12:])) + 23
        return unpack("!I", self.data[ttl_idx:ttl_idx+4])[0]


    def current_ttl(self):
        """Returns an amount of time before ttl exceeding."""
        return self.record_time + self.ttl - time()


    def ttl_exceeded(self):
        """Returns True if a record is not actual."""
        return time() > self.record_time + self.ttl


def get_name(data):
    """Gets a QNAME from a clients data."""
    finish_idx = data.find(pack("!B", 0))
    name = data[:finish_idx]
    return unpack("!{}s".format(len(name)), name)[0]
