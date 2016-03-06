#!/usr/bin/python3
import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.httpserver
from tornado import gen
import cfg
from urllib.parse import urljoin


class ProxyHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def process(self,prefix):
        http_client = tornado.httpclient.HTTPClient()
        url = prefix + self.out_url
        arguments = self.request.query_arguments

        url = urljoin(prefix,self.out_url)
        path,sep,query = self.request.uri.partition('?')

        url = '?'.join([url,query])

        request = tornado.httpclient.HTTPRequest(url=url,
                                                 method=self.request.method,
                                                 headers=self.request.headers,
                                                 body=self.request.body or None)

        try:
            response = http_client.fetch(request)
            return response
        except Exception as e:
            print(e)
            print(url)
            return

    @gen.coroutine
    def upstream(self):
        result = ""
        for pre in cfg.out_prefixes:
            resp = yield self.process(pre)
            if resp and not result: result = resp
        if not result:
            raise tornado.httpclient.HTTPError(500,"Failed reach billing")
        return result

    def set_default_headers(self):
        pass

    @gen.coroutine
    def respond(self,response):
        for (k,v) in sorted(response.headers.get_all()):
            self.add_header(k,v)
        self.write(response.body)

    @gen.coroutine
    def get(self):
        resp = yield self.upstream()
        yield self.respond(resp)

    @gen.coroutine
    def post(self):
        yield self.get()



class SberHandler(ProxyHandler):
    out_url = cfg.sberbank_url

class OsmpHandler(ProxyHandler):
    out_url = cfg.osmp_url





def make_app():
    return tornado.web.Application([
        (cfg.in_prefix+cfg.sberbank_url, SberHandler),
        (cfg.in_prefix+cfg.osmp_url, OsmpHandler),
    ])

if __name__ == "__main__":

    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.bind(cfg.port)
    server.start(0)
    tornado.ioloop.IOLoop.instance().start()
