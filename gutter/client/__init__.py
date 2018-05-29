"""
gutter
~~~~~~~~

:copyright: (c) 2010-2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

try:
    VERSION = __import__('pkg_resources').get_distribution('gutter').version
except Exception as e:
    VERSION = 'unknown'

CLIENT_CACHE = {}


def get_gutter_client(
        alias='default',
        cache=CLIENT_CACHE,
        **kwargs
):
    """
    Creates gutter clients and memoizes them in a registry for future quick access.

    Args:
        alias (str or None): Name of the client. Used for caching.
            If name is falsy then do not use the cache.
        cache (dict): cache to store gutter managers in.
        **kwargs: kwargs to be passed the Manger class.

    Returns (Manager):
        A gutter client.

    """
    from gutter.client.models import Manager

    if not alias:
        return Manager(**kwargs)
    elif alias not in cache:
        cache[alias] = Manager(**kwargs)

    return cache[alias]
