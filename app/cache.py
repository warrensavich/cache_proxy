import requests
import redis
import datetime
import tornado.ioloop
import urllib.parse
import logging
import app.config as config

log = logging.getLogger('proxy')

class CacheManager(object):
    def __init__(self):
        self.redis = redis.Redis(
            host='redis',
            port=6379)
        self.local_cache = {}
        self._purge_local_cache() # get the loop started on init
        self._empty_redis_cache() # see TODO below

    def fetch(self, url):
        if url in self.local_cache:
            log.info("Found %s in Local Cache" % url)
            return self._get_from_local_cache(url)
        redis_cache = self.redis.get(url)
        if redis_cache:
            log.info("Found %s in Redis Cache" % url)
            self._add_to_local(url, redis_cache)
            return redis_cache
        else:
            log.info("URL %s not cound in any caches. Fetching from source" % url)
            return self._fetch_and_cache_from_origin(url)

    def _get_from_local_cache(self, url):
        return self.local_cache[url]['data']

    def _add_to_redis(self, url, data):
        self.redis.set(url, data)

    def _add_to_local(self, url, data, max_age):
        self.local_cache[url] = {
            'data': data,
            'expire_time': datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age)
        }

    def _fetch_from_origin(self, url):
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme:
            return self._fetch_from_origin("http://%s" % url) # a protocol is required
        r = requests.get(url, headers={'User-Agent': config.USER_AGENT})
        if r.status_code == 200:
            return r.content, r.headers
        elif parsed_url.scheme == "http" and r.status_code in [426, 403]:
            # some sites require HTTPS; the RFC 2817 specifies 426 as the code for that,
            # but sometimes 403 is also used
            return self._fetch_from_origin(url.replace("http", "https", 1))
        else:
            return r.content, r.headers # Most websites will return some error page

    def _cache(self, url, data, max_age):
        self._add_to_local(url, data, max_age)
        self._add_to_redis(url, data)

    def _get_max_age_from_headers(self, headers):
        if 'max-age' in headers['Cache-Control']:
            return int(headers['Cache-Control'].split('max-age=')[1].split(',')[0]) # Potential point of failure :(
        else:
            log.info("Cache-Control does not specify max-age")
            return config.LOCAL_CACHE_MAX_AGE

    def _fetch_and_cache_from_origin(self, url):
        data, headers = self._fetch_from_origin(url)
        # TBD Massage the data here a bit to fix relative paths for images, etc. before storing or returning
        if headers['Cache-Control'] not in ['no-cache', 'no-store']:
            log.info("%s Extracting Max Age from Cache-Control Header %s" % (url, headers['Cache-Control']))
            max_age = self._get_max_age_from_headers(headers)
            log.info("Max Age Determined: %s" % max_age)
            self._cache(url, data, max_age)
        else:
            log.info("Server at %s says this cannot be cached" % url)
        return data

    def _purge_local_cache(self):
        log.info("Purge Local Cache Running")
        keys_to_evict = []
        for url, data_dict in self.local_cache.items():
            if data_dict['expire_time'] > datetime.datetime.utcnow():
                keys_to_evict.append(url)

        for key in keys_to_evict:
            del self.local_cache[key]
                
        tornado.ioloop.IOLoop.current().call_later(config.CACHE_PURGE_INTERVAL, lambda: self._purge_local_cache())

    def _empty_redis_cache(self):
        # TODO: Write another service to groom the redis cache, as multiple instances of this web service should
        #       not be responsible for doing that.
        
        # For now this will just purge the redis cache at startup.
        
        log.info("Flushing the Redis Cache")
        self.redis.flushall()
        
        
