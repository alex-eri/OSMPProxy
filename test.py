import cfg
from server import *
import tornado.ioloop
import logging

cfg.port = 8888
cfg.in_prefix = "/billing/paysys/"

cfg.sberbank_url = "sber.cgi"
cfg.osmp_url = "osmp.cgi"

cfg.out_prefixes = [
    "http://localhost:8888/test/main_billing/",
    "http://localhost:8888/test/new_biling/"
]

class EchoTest(tornado.web.RequestHandler):
    def get(self):
        self.write('hello:')
        self.write(self.request.uri)

def make_app():
    return tornado.web.Application([
        (cfg.in_prefix+cfg.sberbank_url, SberHandler),
        (cfg.in_prefix+cfg.osmp_url, OsmpHandler),
        ('/test/.*',EchoTest)
    ])

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.bind(cfg.port)
    server.start(0)
    tornado.ioloop.IOLoop.instance().start()
