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

from bottle import Bottle, request
from bakula.bottle import configuration
from bakula.bottle.errorutils import create_error
from bakula.security.tokenauthplugin import TokenAuthorizationPlugin
import requests
import urlparse

app = Bottle()

configuration.bootstrap_app_config(app)

# Setup authorization plugin
token_secret = app.config.get('token_secret', 'password')
auth_plugin = TokenAuthorizationPlugin(token_secret)
app.install(auth_plugin)

# Set up connection defaults
auth = (app.config.get('registry_username'), app.config.get('registry_password'))
base_url = app.config.get('registry_url', 'https://registry.immuta.com/v1/')

@app.get('/images')
def get_images():
    response = requests.get(urlparse.urljoin(base_url, 'search'))
    response_obj = response.json()
    image_names = map(lambda image: image['name'], response_obj['results'])
    return {'images': image_names}