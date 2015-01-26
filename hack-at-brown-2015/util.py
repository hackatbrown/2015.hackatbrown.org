from google.appengine.api import memcache
import pickle

def memcache_memoize(key):
	def decorator(func):
		def inner_func(*args, **kwargs):
			cache_key = pickle.dumps((key, *args, **kwargs))
			res = memcache.get(cache_key)
			if not res:
				res = func(*args, **kwargs)
				memcache.set(cache_key, res)
			return res
		return inner_func
	return decorator
