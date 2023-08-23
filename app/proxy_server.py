import tornado.web
from app.cache import CacheManager

cm = CacheManager()

class ProxyRequestHandler(tornado.web.RequestHandler):
    def get(self):
        url = self.get_argument('url')
        self.write(cm.fetch(url))
