from peewee import Proxy, Model, CharField, ForeignKeyField
from hashlib import md5
from bakula.bottle import peeweeutils

db = Proxy()

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id = CharField(primary_key=True)
    password = CharField()

class Registration(BaseModel):
    topic = CharField()
    container = CharField()
    creator = ForeignKeyField(User)

    class Meta:
        indexes = (
            # every topic,container tuple should be unique
            (('topic', 'container'), True),
        )

# Helper method for resolving a SelectQuery into the underlying dict objects.
# Useful for building response objects.
#
# Params:
#    query: the SelectQuery object to be iterated over and converted to result
#           dict objects.
def resolve_query(query):
    result = []
    for item in query.dicts():
        result.append(item)
    return result

# Initialize all Models (and their database tables) with a configuration object
# denoting which database should be used.
#
# Params:
#    config: the configuration object for Bakula
def initialize_models(config):
    peeweeutils.get_db_from_config(config, db)

    # Create all of the model tables with silent failures (in case the tables
    # already exist)
    User.create_table(True)
    Registration.create_table(True)

    # TODO make this an admin user
    user = None
    try:
        user = User.get(User.id == 'test')
    except User.DoesNotExist:
        user = User.create(id='test', password=md5('password'))
        user.save()