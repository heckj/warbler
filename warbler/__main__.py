#  Copyright (c) 2020 Joseph Heck. See LICENSE

import sys
import socketserver
import pathlib

from logging.handlers import RotatingFileHandler
import logging.config
import logging

from warbler.version import __version__
from warbler.langserver.jsonrpc import JSONRPC2Connection, ReadWriter, TCPReadWriter
from warbler.langserver.server import LangServer
from warbler.configuration import Configuration

logger = logging.getLogger()

# https://stackoverflow.com/a/47075664
# https://docs.python.org/3.6/library/socketserver.html#socketserver.ForkingMixIn
class ForkingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class LangserverTCPTransport(socketserver.StreamRequestHandler):

    config = None

    def handle(self):
        conn = JSONRPC2Connection(TCPReadWriter(self.rfile, self.wfile))
        s = LangServer(conn=conn, config=self.config)
        s.run()


def main():
    import argparse

    config = Configuration()

    log_fn = pathlib.Path(config.log_path, "warbler-ls.log")
    roll_over = log_fn.exists()

    handler = RotatingFileHandler(log_fn, backupCount=5)
    formatter = logging.Formatter(
        fmt='[%(levelname)-7s] %(asctime)s (%(name)s) %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    if roll_over:
        handler.doRollover()

    # logging.basicConfig(filename=log_fn, filemode="w", level=logging.INFO)
    # logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--mode", default="stdio", help="communication (stdio|tcp)")
    parser.add_argument(
        "--addr", default=4389, help="server listen (tcp)", type=int)
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(level=(logging.DEBUG if args.debug else logging.WARNING))
    logger.addHandler(handler)

    logger.info("Warbler %s: Markdown Passive Voice Language Server", __version__)

    config.initialize()

    if args.mode == "stdio":
        logger.info("Reading on stdin, writing on stdout")
        s = LangServer(
            conn=JSONRPC2Connection(ReadWriter(sys.stdin.buffer, sys.stdout.buffer)),
            config=config)
        s.run()
    elif args.mode == "tcp":
        host, addr = "0.0.0.0", args.addr
        logger.info("Accepting TCP connections on %s:%s", host, addr)
        ForkingTCPServer.allow_reuse_address = True
        ForkingTCPServer.daemon_threads = True
        LangserverTCPTransport.config = config
        s = ForkingTCPServer((host, addr), LangserverTCPTransport)
        try:
            s.serve_forever()
        finally:
            s.shutdown()


if __name__ == "__main__":
    main()
