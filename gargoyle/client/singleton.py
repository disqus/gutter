from gargoyle.client import settings
from gargoyle.client.models import Manager

gargoyle = Manager(storage=settings.manager.storage_engine,
                   autocreate=settings.manager.autocreate,
                   operators=settings.manager.operators,
                   inputs=settings.manager.inputs)
