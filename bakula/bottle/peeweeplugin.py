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
import inspect

import bottle
from peewee import *

class PeeweePlugin(object):
    '''This plugin will take care of working with the peewee database

    Attributes:
        db: the peewee database object
        _auto_commit: whether or not we should auto commit every query
        keyword: the keyword we would like to use to inject our db into
    '''
    name = 'peewee'
    api = 2

    # PluginError is defined to bottle >= 0.10
    if not hasattr(bottle, 'PluginError'):
        class PluginError(bottle.BottleException):
            pass
        bottle.PluginError = PluginError


    def __init__(self, db, auto_commit=True, keyword='db'):
        self.db = db
        self.keyword = keyword
        self._auto_commit = auto_commit

    def setup(self, app):
        '''Make sure that other plugins aren't using the same keyword

        Args:
            app: the bottle application that we will be effecting

        Raises:
            PluginError: If another Peewee plugin is installed and using the
            same keyword.
        '''
        for plugin in app.plugins:
            if not isinstance(plugin, PeeweePlugin):
                continue
            if plugin.keyword == self.keyword:
                msg = "Found another PeeWee plugin configured with same keyword"
                raise PluginError(msg)

    def apply(self, callback, route):
        '''The decorator for the plugin

        This will inject the database into the route if its needed and will only
        connect to the database if the keyword is present in the definition.

        Args:
            callback: the function to call after we've setup the database
            rotue: the route that we are decorating

        Returns:
            the return value of the callback
        '''
        # Check to see if the keyword is in the callbacks arguments
        route_args = inspect.getargspec(route.callback)[0]
        if self.keyword not in route_args:
            return callback

        def wrapper(*args, **kwargs):
            self.db.connect()

            # Inject our database
            kwargs[self.keyword] = self.db

            try:
                rv = callback(*args, **kwargs)
                if self._auto_commit:
                    self.db.commit()
            except Exception, e:
                self.db.rollback()
                raise bottle.HTTPError(500, "Database Error: %s" % str(e), e)
            finally:
                self.db.close()
            return rv

        return wrapper


