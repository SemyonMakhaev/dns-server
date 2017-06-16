#!/usr/bin/env python3
"""A caching DNS-server realization."""
import sys
import logging

from socket import gethostbyname, gaierror, socket, error, AF_INET, SOCK_DGRAM
from select import select
from argparse import ArgumentParser
from request_server import RequestServer, DNS_PORT


CLOSING_COMMAND = "avada kedavra"


def main():
    """DNS-requests receiving and responses sending. Also caching."""
    host, forwarder_host, forwarder_port = argument_parse()
    try:
        host = gethostbyname(host)
        forwarder_host = gethostbyname(forwarder_host)
        forwarder_port = int(forwarder_port)
    except gaierror:
        logging.error("Incorrect address.")
        sys.exit(0)
    except ValueError:
        logging.error("Incorrect port.")
        sys.exit(0)
    forwarder = (forwarder_host, forwarder_port)

    sock = socket(AF_INET, SOCK_DGRAM)
    try:
        sock.bind((host, DNS_PORT))
    except error:
        logging.error("Cannot assign requested address.")
        sock.close()
        sys.exit(0)

    print("Server has bound ({}, {})".format(host, DNS_PORT))
    print('For connection closing use "{}" command'.format(CLOSING_COMMAND))

    mainloop = True
    requests_servers = []

    try:
        while mainloop:
            rsocks = select([sock, sys.stdin], [], [], 0.01)[0]
            if sock in rsocks:
                data, host_port = sock.recvfrom(4096)
                server = RequestServer(sock, data, host_port, forwarder)
                requests_servers.append(server)
                server.start()
            if sys.stdin in rsocks and CLOSING_COMMAND.startswith(input()):
                break

            trash = []# Working threads analysing.
            for server in requests_servers:
                if server.recursion:
                    # A case of recurrent queries.
                    logging.error("Cannot work in this conditions")
                    mainloop = False

                elif not server.is_alive():
                    trash.append(server)

            for server in trash:
                requests_servers.remove(server)
    finally:
        sock.close()
        print("Connection has been closed.")


def argument_parse():
    """Arguments parsing."""
    parser = ArgumentParser(prog="python3 dns_cache.py", \
        description="A caching DNS-server.", \
        epilog="(c) Semyon Makhaev, 2016. All rights reserved.")
    parser.add_argument("host", type=str, default="127.0.0.1", nargs='?', \
        help="DNS-server address or domain name. A default value is 127.0.0.1")
    parser.add_argument("forwarder_host", type=str, default="8.8.8.8", nargs="?", \
        help="A forwarding DNS-server address. A default value is 8.8.8.8")
    parser.add_argument("forwarder_port", type=str, default="53", nargs="?", \
        help="A forwarding DNS-server port. A default value is 53.")
    args = parser.parse_args()
    return args.host, args.forwarder_host, args.forwarder_port


if __name__ == "__main__":
    main()
