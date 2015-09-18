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
from bakula.models import Registration, User, resolve_query
from bakula.bottle.errorutils import create_error
from bakula.security.tokenauthplugin import TokenAuthorizationPlugin
from peewee import IntegrityError

app = Bottle()

configuration.bootstrap_app_config(app)

# Setup authorization plugin
token_secret = app.config.get('token_secret', 'password')
auth_plugin = TokenAuthorizationPlugin(token_secret)
app.install(auth_plugin)

@app.get('/registration')
def get_registrations():
    return {'results': resolve_query(Registration.select())}

@app.get('/registration/<registration_id>')
def get_registration(registration_id):
    try:
        registration = Registration.get(Registration.id == registration_id)
        return registration._data
    except Registration.DoesNotExist:
        return create_error(status_code=404,
                            message='A registration with the ID %s does not exist' % (registration_id))

@app.post('/registration')
def create_registration(user):
    registration_dict = request.json
    registration_dict['creator'] = user

    new_registration = Registration(**registration_dict)
    try:
        new_registration.save()
        return {'id': new_registration.id}
    except IntegrityError:
        return create_error(status_code=400,
                            message='A registration for topic %s with container %s already exists' %
                            (registration_dict['topic'], registration_dict['container']))

@app.delete('/registration/<registration_id>')
def delete_registration(registration_id, user):
    try:
        registration = Registration.get(Registration.id == registration_id,
                                        Registration.creator == user)
        id = registration.id
        registration.delete_instance()
        return {'id': id}
    except Registration.DoesNotExist:
        return create_error(status_code=404,
                            message='A registration with the ID %s does not exist' % (registration_id))
