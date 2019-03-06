#!/usr/bin/env python
# -*- coding: utf-8 -*-
from prometheus_client import CollectorRegistry, PlatformCollector
from prometheus_client import ProcessCollector, GCCollector
from prometheus_client import Counter, Summary, Info, Histogram, Enum
from prometheus_client.utils import INF

from prometheus_client.exposition import choose_encoder

from http.server import BaseHTTPRequestHandler, HTTPServer

import random

c = Counter('requests_total', 'Total number of requests', registry=None)
s = Summary('requests_time', '', registry=None)
info = Info('author_info', 'author infomation', registry=None)
info.info({'name': 'jeffrey4l', 'email': 'abc@gmail.com'})

h = Histogram('random_integer', 'Request size (bytes)',
              buckets=[0, 2, 4, 6, 8, INF],
              registry=None)

e = Enum('task_state', 'Description of enum',
         states=['starting', 'running', 'stopped'])

platform_collector = PlatformCollector(registry=None)
p_collector = ProcessCollector(registry=None)

collectors = [c, s, info, h, e, platform_collector, p_collector]
global_registry = CollectorRegistry()

gc_collector = GCCollector(registry=global_registry)


class MyHandler(BaseHTTPRequestHandler):

    @s.time()
    def do_GET(self):
        c.inc()
        e.state(random.choice(['starting', 'running', 'stopped']))
        h.observe(random.randint(1, 11))
        registry = CollectorRegistry(auto_describe=True)
        for i in collectors:
            registry.register(i)
        encoder, content_type = choose_encoder(self.headers.get('Accept'))
        output = encoder(registry)
        output2 = encoder(global_registry)
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(output)
        self.wfile.write(output2)


def main():
    server = HTTPServer(('0.0.0.0', 7778), MyHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
