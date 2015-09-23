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

import unittest
from bakula import models
from bakula.services import metrics
from bakula.security import tokenutils, iam
from webtest import TestApp
import time
import numpy
import docker

test_app = TestApp(metrics.app)

def get_current_time():
    return int(time.time() * 1000)

class MetricsTest(unittest.TestCase):
    auth_header = None
    test_user = None
    topic = 'metric_test'
    container = 'ericjperry/busybox-sleep'
    registration_id = None

    @classmethod
    def setUpClass(self):
        models.initialize_models({'database.name': ':memory:',
                                  'database.type': 'sqlite'})
        iam.create('user', 'some_password')
        MetricsTest.test_user = models.User.get(models.User.id == 'user')
        MetricsTest.auth_header = {
            'Authorization': tokenutils.generate_auth_token(
                'password',
                MetricsTest.test_user.id,
                120)
        }
        MetricsTest.registration_id = models.Registration.create(
            topic=MetricsTest.topic,
            container=MetricsTest.container,
            creator=MetricsTest.test_user
        ).id

    def setUp(self):
        models.Metric.delete().execute()
        models.Event.delete().execute()

    def test_get_metrics_no_containers(self):
        # Add some metrics to the DB
        topic = 'metric_test'
        cpu_values = [0.0143, 0.0148, 0.0153]
        memory_values = [0.0045, 0.004535, 0.00612]
        duration_values = [1649, 2195]
        for value in cpu_values:
            models.Metric.create(
                topic=MetricsTest.topic,
                container=MetricsTest.container,
                timestamp=get_current_time(),
                name='cpu',
                value=value
            )
        for value in memory_values:
            models.Metric.create(
                topic=MetricsTest.topic,
                container=MetricsTest.container,
                timestamp=get_current_time(),
                name='memory',
                value=value
            )
        for value in duration_values:
            models.Event.create(
                topic=MetricsTest.topic,
                container=MetricsTest.container,
                timestamp=get_current_time(),
                duration=value
            )

        response = test_app.get(
            '/metrics/' + str(MetricsTest.registration_id),
            headers=MetricsTest.auth_header
        )

        self.assertEquals(response.status_int, 200)
        numpy.testing.assert_almost_equal(response.json['duration'], sum(duration_values)/len(duration_values))
        numpy.testing.assert_almost_equal(response.json['cpu'], sum(cpu_values)/len(cpu_values))
        numpy.testing.assert_almost_equal(response.json['memory'], sum(memory_values)/len(memory_values))
        self.assertEquals(response.json['containers'], 0)

        self.assertEquals(len(response.json['events']), 1)
        for key in response.json['events']:
            self.assertEquals(response.json['events'][key], 2)

    def test_get_metrics_one_container(self):
        # Add some metrics to the DB
        topic = 'metric_test'
        cpu_values = [0.0143, 0.0148, 0.0153]
        memory_values = [0.0045, 0.004535, 0.00612]
        duration_values = [1649, 2195]
        for value in cpu_values:
            models.Metric.create(
                topic=MetricsTest.topic,
                container=MetricsTest.container,
                timestamp=get_current_time(),
                name='cpu',
                value=value
            )
        for value in memory_values:
            models.Metric.create(
                topic=MetricsTest.topic,
                container=MetricsTest.container,
                timestamp=get_current_time(),
                name='memory',
                value=value
            )
        for value in duration_values:
            models.Event.create(
                topic=MetricsTest.topic,
                container=MetricsTest.container,
                timestamp=get_current_time(),
                duration=value
            )

        client = docker.Client()
        client.pull(MetricsTest.container, tag='latest')
        container = client.create_container(
            image=MetricsTest.container,
            labels={
                'topic': MetricsTest.topic
            }
        )
        client.start(container['Id'])

        # Give the container a few seconds to start up
        time.sleep(2)
        response = test_app.get(
            '/metrics/' + str(MetricsTest.registration_id),
            headers=MetricsTest.auth_header
        )

        self.assertEquals(response.status_int, 200)
        numpy.testing.assert_almost_equal(response.json['duration'], sum(duration_values)/len(duration_values))
        numpy.testing.assert_almost_equal(response.json['cpu'], sum(cpu_values)/len(cpu_values))
        numpy.testing.assert_almost_equal(response.json['memory'], sum(memory_values)/len(memory_values))
        self.assertEquals(response.json['containers'], 1)

        self.assertEquals(len(response.json['events']), 1)
        for key in response.json['events']:
            self.assertEquals(response.json['events'][key], 2)

        # Wait for container to stop running and get cleaned up
        time.sleep(10)

if __name__ == '__main__':
    unittest.main()
