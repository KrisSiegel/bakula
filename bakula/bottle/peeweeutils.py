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

from peewee import *

def get_db_from_config(config, proxy=None):
    '''This method will return a peewee db object from a config dictionary

    Currently we only support postgres and sqlite
    Args:
        config: the configuration dictionary
        proxy: a peewee proxy which we can initialize

    Raises:
        RuntimeError if no config is given, if no databaseType is found,
        or if no database is found

    Returns:
        A peewee database object or none if we are initialize a proxy object
    '''
    if not config:
        raise RuntimeError('No configuration was given!')

    db_args = None
    for db_type in ['postgres', 'sqlite']:
        db_args = config.get(db_type, None)
        if db_args:
            break

    # We have exahusted our dictionary
    if not db_args:
        raise RuntimeError("Could not find database information!")


    database = db_args.get('database', None)
    if not database:
        raise RuntimeError('No database was found!')

    del db_args['database']

    # Create a new database based on our type
    db = None
    if db_type == 'postgres':
        db = PostgresqlDatabase(database, **db_args)
    elif db_type == 'sqlite':
        db = SqliteDatabase(database, **db_args)

    if proxy:
        proxy.initialize(db)
        return

    return db
