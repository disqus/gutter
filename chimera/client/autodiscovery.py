import logging


logger = logging.getLogger(__name__)


def discover():
    """
    Auto-discover any Chimera configuration present in the django
    INSTALLED_APPS.
    """
    from django.conf import settings
    from django.utils.importlib import import_module

    for app in settings.INSTALLED_APPS:
        module = '%s.chimera' % app

        try:
            import_module(module)
            logger.info('Successfully autodiscovered %s' % module)
        except:
            logger.info('Error autodisvoering %s' % module)
