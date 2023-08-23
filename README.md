# Tornado Cache Proxy
A caching proxy server written in python leveraging redis and tornado

# Setup
Clone this repository into a machine with Docker installed and run the following: 

* docker-compose build 
* docker-compose up -d

This will pull in the redis image and tbe python alpine image and build the container for the web server on top of the python alpine image. After the second command completes the proxy server can be used by going to localhost in any browser and supplying it with the URL you wish to load as a query parameter such as the following:

* localhost/proxy?url=www.google.com

# Caveats

* This service does not yet properly proxy content such as images or other static files with a relative path.
* This service uses both a local cache and a redis cache prior before falling back to the source site. The local cache is groomed according to the times layed out in the app/config.py module, but redis is just cleared at startup and content isn't managed so it does not expire.
