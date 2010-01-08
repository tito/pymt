'''
Cache Manager: a way to cache things, and delete them automaticly
'''

__all__ = ('Cache', )

from pymt.logger import pymt_logger
from pymt.clock import getClock

class Cache:
    '''Cache, a manager to cache object'''

    _categories = {}
    _objects = {}

    @staticmethod
    def register(category, limit=None, timeout=None):
        '''Register a new category in cache, with limit

        :Parameters:
            `category` : str
                Identifier of the category
            `limit` : int (optionnal)
                Maximum number of object in the cache.
                If None, no limit is applied.
            `timeout` : double (optionnal)
                Time to delete the object when it's not used.
                if None, no timeout is applied.
        '''
        Cache._categories[category] = {
            'limit': limit,
            'timeout': timeout
        }
        Cache._objects[category] = {}
        pymt_logger.debug('Cache: register <%s> with limit=%s, timeout=%ss' %
            (category, str(limit), str(timeout)))

    @staticmethod
    def append(category, key, obj, timeout=None):
        '''Add a new object in the cache.

        :Parameters:
            `category` : str
                Identifier of the category
            `key` : str
                Uniq identifier of the object to store
            `obj` : object
                Object to store in cache
            `timeout` : double (optionnal)
                Custom time to delete the object if it's not used.
        '''
        if not category in Cache._categories:
            pymt.pymt_logger.warning('Cache: category <%s> not exist' % category)
            return
        if timeout is None:
            timeout = Cache._categories[category]['timeout']
        Cache._objects[category][key] = {
            'object': obj,
            'timeout': timeout,
            'lastaccess': getClock().get_time(),
            'timestamp': getClock().get_time()
        }

    @staticmethod
    def get(category, key, default=None):
        '''Get a object in cache.

        :Parameters:
            `category` : str
                Identifier of the category
            `key` : str
                Uniq identifier of the object to store
            `default` : anything, default to None
                Default value to be returned if key is not found
        '''
        try:
            Cache._objects[category][key]['lastaccess'] = getClock().get_time()
            return Cache._objects[category][key]['object']
        except:
            return default

    @staticmethod
    def get_timestamp(category, key, default=None):
        '''Get the object timestamp in cache.
        
        :Parameters:
            `category` : str
                Identifier of the category
            `key` : str
                Uniq identifier of the object to store
            `default` : anything, default to None
                Default value to be returned if key is not found
        '''
        try:
            return Cache._objects[category][key]['timestamp']
        except:
            return default

    @staticmethod
    def get_lastaccess(category, key, default=None):
        '''Get the object last access time in cache.
        
        :Parameters:
            `category` : str
                Identifier of the category
            `key` : str
                Uniq identifier of the object to store
            `default` : anything, default to None
                Default value to be returned if key is not found
        '''
        try:
            return Cache._objects[category][key]['lastaccess']
        except:
            return default

    @staticmethod
    def remove(category, key=None):
        '''Purge the cache

        :Parameters:
            `category` : str (optionnal)
                Identifier of the category
            `key` : str (optionnal)
                Uniq identifier of the object to store
        '''
        try:
            if key is not None:
                del Cache._objects[category][key]
            else:
                Cache._objects[category] = {}
        except:
            pass

    @staticmethod
    def _purge_by_timeout(*largs):

        curtime = getClock().get_time()

        for category in Cache._objects:

            timeout = Cache._categories[category]['timeout']

            for key in Cache._objects[category].keys():

                lastaccess  = Cache._objects[category][key]['lastaccess']
                objtimeout  = Cache._objects[category][key]['timeout']

                # take the object timeout if available
                if objtimeout is not None:
                    timeout = objtimeout

                # no timeout, cancel
                if timeout is None:
                    continue

                if curtime - lastaccess > timeout:
                    del Cache._objects[category][key]

    @staticmethod
    def print_usage():
        print 'Cache usage :'
        for category in Cache._categories:
            print ' * %s : %d / %s, timeout=%s' % (
                category.capitalize(),
                len(Cache._objects[category]),
                str(Cache._categories[category]['limit']),
                str(Cache._categories[category]['timeout'])
            )

# install the schedule clock for purging
getClock().schedule_interval(Cache._purge_by_timeout, 1)
