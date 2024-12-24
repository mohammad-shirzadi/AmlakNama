class PGISrouter:
    def db_for_read(self, model,**hints):
        if model._meta.app_label == "explore":
            return 'PGIS'
        elif model._meta.app_label == "updateData":
            return 'default'
        return None
    def db_for_write(self, model, **hints):
        if model._meta.app_label == "explore":
            return 'PGIS'
        elif model._meta.app_label == "updateData":
            return 'default'
        return None
    def allow_relation(self, obj1, obj2, **hints):
        db_set = ['default', 'PGIS']
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    def allow_migration(self, db, app_label, model_name=None, **hint):
        if app_label == 'explore':
            return db == 'PGIS'
        elif app_label == "updateData":
            return db == "default"
        #return None
