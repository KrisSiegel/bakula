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
from bottle import Bottle
from bakula.bottle import configuration
from bakula.security.tokenauthplugin import TokenAuthorizationPlugin

def init_app(app):
    configuration.bootstrap_app_config(app)

    # Setup authorization plugin
    token_secret = app.config.get('token_secret', 'password')
    auth_plugin = TokenAuthorizationPlugin(token_secret)
    app.install(auth_plugin)

    return auth_plugin