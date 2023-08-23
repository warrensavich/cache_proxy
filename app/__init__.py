import tornado.web
from app.proxy_server import ProxyRequestHandler
import app.config as config

def interface():
    return tornado.web.Application([
        (r"/proxy", ProxyRequestHandler)
        ], debug=config.DEBUG)
