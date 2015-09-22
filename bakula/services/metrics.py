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
from bakula.models import Metric, Registration, Event
from bakula.bottle.errorutils import create_error
from bakula.security.tokenauthplugin import TokenAuthorizationPlugin
from peewee import fn
import datetime
import time

app = Bottle()

configuration.bootstrap_app_config(app)

# Setup authorization plugin
token_secret = app.config.get('token_secret', 'password')
auth_plugin = TokenAuthorizationPlugin(token_secret)
app.install(auth_plugin)

MILLISECONDS_IN_DAY = 86400000

@app.get('/metrics/<registration_id>')
def get_metrics(registration_id):
    # Collect and return the following metrics:
    #    - Current number of containers running for this registration
    #    - Average CPU usage for this registration
    #    - Average memory usage for this registration
    #    - Average processing time for this registration
    #    - Number of events per day for the last week
    registration = Registration.get(Registration.id == registration_id)

    stats = Metric.select(
        Metric.name,
        fn.AVG(Metric.value).alias('average')
    ).where(
        Metric.topic == registration.topic,
        Metric.container == registration.container
    ).group_by(Metric.name)

    # Use the beginning of the day tomorrow as a starting point (for full
    # days)
    tomorrow = int(datetime.datetime.combine(
        datetime.date.today() + datetime.timedelta(days=1),
        datetime.time.min
    ).timetuple() * 1000)

    # Get the starting point (one week ago)
    one_week_ago = tomorrow - (7 * MILLISECONDS_IN_DAY)
    events = Event.select(
        fn.ROUND(Event.timestamp/MILLISECONDS_IN_DAY)*MILLISECONDS_IN_DAY,
        fn.AVG(Event.duration).alias('avgDuration')
    ).where(
        Event.topic == registration.topic,
        Event.container == registration.container,
        Event.timestamp < tomorrow,
        Event.timestamp >= one_week_ago
    ).group_by('avgDuration')