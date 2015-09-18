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
import argparse
import sys

from bottle import Bottle, run
from bakula.services import healthcheck, registration
from bakula.models import initialize_models
from bakula.bottle import configuration

app = Bottle()

# To add a subapplication simply do the necessary imports and add the
# application to the list below
sub_apps = [
    healthcheck.app,
    registration.app
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bakula server')
    parser.add_argument('-H', '--host', help='host address',
                        default='localhost')
    parser.add_argument('-P', '--port', help='port of the bakula server',
                        default='5000')

    args = parser.parse_args()

    for sub_app in sub_apps:
        app.merge(sub_app)

    configuration.bootstrap_app_config(app)
    initialize_models(app.config)
    run(app, host=args.host, port=args.port)
