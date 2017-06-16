#!/usr/bin/env python3
"""A supporting module for DNS-server realization."""
from socket import socket, AF_INET, SOCK_DGRAM, timeout
from threading import Thread, Lock
from struct import pack, unpack
from time import time
from logging import info, warning, error
from cache_record import get_name


DNS_PORT = 53
TIMEOUT = 3

# A cache realizaion.
CACHE = {}
CACHE_LOCK = Lock()

# Queries ID saving for recurrent refusing.
QUERIES_ID = []


class RequestServer(Thread):
    """The tool for a clients request serving."""
    def __init__(self, sock, request, host_port, forwarder):
        super(RequestServer, self).__init__()
        self.sock = sock
        self.request = request
        self.host_port = host_port
        self.forwarder = forwarder
        self.recursion = False


    def run(self):
        """
        Package parsing, cache checking and a responce sending.
        Forwarder requesting if there is no record in cache.
        """
        key = self.request[2:]

        with CACHE_LOCK:

            if key in CACHE and time() < CACHE[key][1] + CACHE[key][2]:
                reply = self.get_from_cache(key)

            else:
                package_id = self.request[:2]# Transaction id.
                if package_id in QUERIES_ID:
                    error("Recurrent queries detected")
                    self.recursion = True
                    return

                else:
                    QUERIES_ID.append(package_id)
                    reply = self.forwarder_request()
                    if reply is None:
                        return

                CACHE[key] = [reply[2:], get_package_ttl(reply), time()]

        self.sock.sendto(reply, self.host_port)

        info("Served %s", self.host_port[0])


    def get_from_cache(self, key):
        """Returns a record from cache by key."""
        response = CACHE[key][0]
        ttl = pack("!I", int(CACHE[key][1] + CACHE[key][2] - time()))
        identifier = self.request[:2]
        data = identifier + response

        answers_count = unpack("!H", data[6:8])[0]# Answer RRs.
        current_idx = len(get_name(data[12:])) + 23

        # Changing all of TTLs in the package.
        for _ in range(answers_count):
            data = data[:current_idx] + ttl + data[current_idx+4:]
            data_length = unpack("!H", data[current_idx+4:current_idx+6])[0]
            current_idx += data_length + 12

        return data


    def forwarder_request(self):
        """A request to forwarder sending."""
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.settimeout(TIMEOUT)

        try:
            sock.sendto(self.request, self.forwarder)
            reply = sock.recv(512)

        except timeout:
            warning("Cannot get reply from forwarder")
            return

        finally:
            sock.close()

        return reply


def get_package_ttl(data):
    """Returns a ttl of received package."""
    ttl_idx = len(get_name(data[12:])) + 23
    return unpack("!I", data[ttl_idx:ttl_idx+4])[0]
