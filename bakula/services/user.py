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
from bakula.security import iam, tokenutils
from bakula.security.tokenauthplugin import TokenAuthorizationPlugin
from bakula.bottle.errorutils import create_error

app = Bottle()

configuration.bootstrap_app_config(app)

# Setup authorization plugin
token_secret = app.config.get('token_secret', 'password')
auth_plugin = TokenAuthorizationPlugin(token_secret)
app.install(auth_plugin)

@app.post('/login', skip=[auth_plugin])
def login():
    id = request.json['id']
    password = request.json['password']

    if iam.authenticate(id, password):
        return {
            'token': tokenutils.generate_auth_token(token_secret, id, 3600)
        }
    else:
        return create_error(401, 'Invalid username or password')

@app.post('/user')
def create_user(user):
    if user == 'admin':
        id = request.json['id']
        password = request.json['password']

        created = iam.create(id, password)
        if created:
            return {'id': id}
        else:
            return create_error(400,
                                'A user already exists with id %s' %
                                (id))
    else:
        return create_error(403, 'Only the admin user can create new users')
