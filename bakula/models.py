# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing,
#   software distributed under the License is distributed on an
#   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#   KIND, either express or implied.  See the License for the
#   specific language governing permissions and limitations
#   under the License.
from peewee import (Proxy, Model, CharField, ForeignKeyField, IntegerField,
                    BooleanField, DecimalField)
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
    privileged = BooleanField(default=False)
    threshold = IntegerField(default=0)
    timeout = IntegerField(default=0)
    creator = ForeignKeyField(User)

    class Meta:
        indexes = (
            # every topic,container tuple should be unique
            (('topic', 'container'), True),
        )

class Metric(BaseModel):
    topic = CharField()
    container = CharField()
    timestamp = IntegerField()
    name = CharField()
    value = DecimalField()

class Event(BaseModel):
    topic = CharField()
    container = CharField()
    timestamp = IntegerField()
    duration = IntegerField()

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
    Metric.create_table(True)
    Event.create_table(True)

    # The first user in the DB will be the admin user. Ignore errors.
    from bakula.security import iam
    iam.create('admin', config.get('admin_password', 'secret'))
