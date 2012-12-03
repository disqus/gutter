from chimera.client import settings
from chimera.client.models import Manager

chimera = settings.manager.default or Manager(
    storage=settings.manager.storage_engine,
    autocreate=settings.manager.autocreate,
    inputs=settings.manager.inputs
)
