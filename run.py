import tornado.web
import tornado.ioloop
import requests
import app

if __name__ == "__main__":
    tornado_app = app.interface()
    tornado_app.listen(80)
    tornado.ioloop.IOLoop.instance().start()
