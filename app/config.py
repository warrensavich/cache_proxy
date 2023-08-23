import logging
import datetime

logging.basicConfig(level=logging.DEBUG)

DEBUG = True

CACHE_PURGE_INTERVAL = 60 # one minute
LOCAL_CACHE_MAX_AGE  = 1800
LOCAL_CACHE_MAX_UNTOUCHED_LIFE = datetime.timedelta(minutes=5)
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
