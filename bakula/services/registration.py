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
from bottle import Bottle, HTTPResponse, request
from bakula.bottle import configuration
from bakula.models import Registration, User, resolve_query
from bakula.bottle.errorutils import create_error
from peewee import IntegrityError

app = Bottle()

configuration.bootstrap_app_config(app)

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
def create_registration():
    registration_dict = request.json
    # TODO this should be auto-injected
    registration_dict['creator'] = User.get(User.id == 'test')

    new_registration = Registration(**registration_dict)
    try:
        new_registration.save()
        return {'id': new_registration.id}
    except IntegrityError:
        return create_error(status_code=400,
                            message='A registration for topic %s with container %s already exists' %
                            (registration_dict['topic'], registration_dict['container']))

@app.delete('/registration/<registration_id>')
def delete_registration(registration_id):
    try:
        registration = Registration.get(Registration.id == registration_id)
        id = registration.id
        registration.delete_instance()
        return {'id': id}
    except Registration.DoesNotExist:
        return create_error(status_code=404,
                            message='A registration with the ID %s does not exist' % (registration_id))