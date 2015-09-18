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

# Using simplejson here because it doesn't do any json unicode silliness
# which mucks with the app.config.load_dict method. See https://github.com/bottlepy/bottle/issues/720.
# The issue has actually been fixed and closed, but they haven't tagged a new version since December
# (which didn't have the fix). So, remove this and use the regular json module once bottle has
# been updated beyond 0.12.8.
import simplejson
import logging
import os

from bottle import Bottle

logger = logging.getLogger(__name__)

def bootstrap_app_config(app):
    """Bootstraps the application configuration

    Method will deserialize a JSON file into a dictionary and will load that into
    Bottle's configuration object. It gets the JSON file's path by attempting to
    read the path from an environment varabile. If the environment variable
    isn't set then it will default to the file 'bakula_config.json' in the
    current working directory.

    Args:
        app: a instance of a bottle application

    Raises:
        ValueError: if app is not a instance of a bottle object
        IOError: if the json_file does not exist
    """

    json_file = os.getenv('BAKULA_CFG_FILE', 'bakula_config.json')

    if not os.path.exists(json_file):
        msg = "Can not read configuration file %s using default configuration" \
                % json_file
        logger.warn(msg)
        return

    if not isinstance(app, Bottle):
        raise ValueError("App is not an instance of Bottle!")

    logger.info("Attempting load configuration from %s" % json_file)
    json_obj = None
    with open(json_file, 'r') as json_contents:
        json_obj = simplejson.load(json_contents)

    app.config.load_dict(json_obj)
