from gutter.client import settings
from gutter.client.models import Manager

gutter = settings.manager.default or Manager(
    storage=settings.manager.storage_engine,
    autocreate=settings.manager.autocreate,
    inputs=settings.manager.inputs
)
