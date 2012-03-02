from gargoyle.client.settings import manager
from gargoyle.client.models import Manager

gargoyle = Manager(storage=manager.storage_engine,
                   autocreate=manager.autocreate)
