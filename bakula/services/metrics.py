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
from bakula.docker import dockeragent
from bakula.models import Metric, Registration, Event, resolve_query
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

# Create a DockerAgent object to grab currently running containers.
# Turn off the monitoring thread.
docker_agent = dockeragent.DockerAgent(registry_host=app.config.get("registry.host", None),
    username=app.config.get("registry.username", None),
    password=app.config.get("registry.password", None),
    docker_timeout=app.config.get("docker.timeout", 2),
    monitor_thread=False)

MILLISECONDS_IN_DAY = 86400000

@app.get('/metrics/<registration_id>')
def get_metrics(registration_id):
    # Collect and return the following metrics:
    #    - Current number of containers running for this registration
    #    - Average CPU usage for this registration
    #    - Average memory usage for this registration
    #    - Average processing time for this registration
    #    - Number of events per day for the last week
    result = {}
    registration = Registration.get(Registration.id == registration_id)

    stats = Metric.select(
        Metric.name,
        fn.AVG(Metric.value).alias('average')
    ).where(
        Metric.topic == registration.topic,
        Metric.container == registration.container
    ).group_by(Metric.name)

    # Add to the result object
    for stat in stats:
        result[stat.name] = stat.average

    # Use the beginning of the day as a starting point (for full
    # days)
    today_dt = datetime.datetime.combine(
        datetime.date.today(),
        datetime.time.min
    )
    today = int(time.mktime(today_dt.timetuple()) * 1000)

    # Get the starting point (one week ago)
    one_week_ago = today - (7 * MILLISECONDS_IN_DAY)
    events = Event.select(
        # In order to query by date intervals, we need to divide by one day
        # worth of milliseconds, round to the nearest whole number, then
        # multiply the milliseconds back in. This will create intervals and
        # normalize the returned values.
        (fn.ROUND(Event.timestamp/MILLISECONDS_IN_DAY) * MILLISECONDS_IN_DAY).alias('date'),
        fn.COUNT(Event.id).alias('events')
    ).where(
        Event.topic == registration.topic,
        Event.container == registration.container,
        Event.timestamp >= one_week_ago
    ).group_by('date')

    # Add to the result object
    result['events'] = {}
    for event in events:
        result['events'][int(event.date)] = event.events

    avg_duration = Event.select(fn.AVG(Event.duration)).where(
        Event.topic == registration.topic,
        Event.container == registration.container
    ).scalar()
    result['duration'] = avg_duration

    result['containers'] = docker_agent.container_count(registration.topic, registration.container)

    return result
