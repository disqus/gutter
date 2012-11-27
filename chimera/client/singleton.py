from chimera.client import settings
from chimera.client.models import Manager

print settings.manager.default
chimera = settings.manager.default or Manager(
    storage=settings.manager.storage_engine,
    autocreate=settings.manager.autocreate,
    operators=settings.manager.operators,
    inputs=settings.manager.inputs
)
