from peewee import *
from hashlib import md5

# TODO: once the swappable database is completed
# from bakula.database import db

db = SqliteDatabase('bakula.db')

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

# Create all of the model tables with silent failures (in case the tables
# already exist)
User.create_table(True)
Registration.create_table(True)

# TODO testing
user = None
try:
    user = User.get(User.id == 'test')
except User.DoesNotExist:
    print "user didn't exist"
    user = User.create(id='test', password=md5('password'))
    user.save()