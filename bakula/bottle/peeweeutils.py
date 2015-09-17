# Copyright 2015 Immuta, Inc. Licensed under the Immuta Software License
# Version 0.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#
#    http://www.immuta.com/licenses/Immuta_Software_License_0.1.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from peewee import *

def get_db_from_config(config):
    '''This method will return a peewee db object from a config dictionary

    Currently we only support postgres and sqlite
    Args:
        config: the configuration dictionary

    Raises:
        RuntimeError if no config is given, if no databaseType is found,
        or if no database is found

    Returns:
        A peewee database object
    '''
    if not config:
        raise RuntimeError('No configuration was given!')

    # Get our database type
    db_type = config.get('databaseType', None)

    if not db_type in ['postgres', 'sqlite']:
        raise RuntimeError("Unknown database %s" % db_type)

    db_args = {}
    prefix = "%s_" % db_type
    database = None
    for key in config.keys():
        if key.startswith(prefix):
            arg_value = config[key]
            arg_key = key[len(prefix):]
            if arg_key == 'database':
                database = arg_value
            else:
                db_args[arg_key] = arg_value

    if not database:
        raise RuntimeError('No database string was sepcified!')

    # Create a new database based on our type
    if db_type == 'postgres':
        return PostgresqlDatabase(database, **db_args)

    return SqliteDatabase(database, **db_args)
