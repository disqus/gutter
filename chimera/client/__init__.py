"""
chimera
~~~~~~~~

:copyright: (c) 2010-2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

try:
    VERSION = __import__('pkg_resources').get_distribution('chimera').version
except Exception, e:
    VERSION = 'unknown'

from chimera.client.autodiscovery import discover as autodiscover
