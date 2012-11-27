from gargoyle.client import settings
from gargoyle.client.models import Manager

print settings.manager.default
gargoyle = settings.manager.default or Manager(
    storage=settings.manager.storage_engine,
    autocreate=settings.manager.autocreate,
    operators=settings.manager.operators,
    inputs=settings.manager.inputs
)
