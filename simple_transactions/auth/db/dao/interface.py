from .database import Database

def repository_for(model):
    def decorator(cls):
        orig_init = cls.__init__

        def __init__(self, database: Database, *args, **kwargs):
            super(cls, self).__init__(database, model)
            orig_init(self, database, model, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return decorator
