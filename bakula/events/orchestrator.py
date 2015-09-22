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
from bakula.events.inboxer import Inboxer
from bakula.docker.dockeragent import DockerAgent
from threading import Timer
from bakula.models import Registration, resolve_query
from calendar import timegm
from time import gmtime
from uuid import uuid4

TIMER_INTERVAL = 10.0

# This class handles the event handling of the inboxer and, when a threshold is hit,
# it promotes the appropriate files as an inbox or a docker container then fires the
# docker container.
class Orchestrator:
    def __init__(self, inboxer=Inboxer(), docker_agent=None):
        self.inboxer = inboxer
        self.inboxer.on("received", self.__handle_inbox_received_event)
        self.docker_agent = docker_agent
        if self.docker_agent is None:
            self.docker_agent = DockerAgent()

        # Setup pending queue
        self.pending = { }
        self.__process_pending()

    # Get listing of registered containers filtered by topic
    def __get_registered_containers(self, topic):
        return resolve_query(Registration.select().where(Registration.topic == topic))

    # Clear the pending queue of a specific topic
    def __clear_pending(self, topic, container_name):
        if topic is not None and topic in self.pending:
            if container_name is not None and container_name in self.pending[topic]:
                del self.pending[topic][container_name]

    # Iterate through the self.pending queue and act on anything queued
    # that has passed its timer
    def __process_pending(self):
        for topic in self.pending:
            for container in self.pending[topic]:
                if self.__get_current_time_in_seconds() > self.pending[topic][container]:
                    # It's go time!
                    self.__process(topic, container)
        self.interval_timer = Timer(TIMER_INTERVAL, self.__process_pending)
        self.interval_timer.start()

    def __process(self, topic, container_name):
        self.__clear_pending(topic, container_name) # Clear the topic so this isn't hit multiple times

        # Promote all files in the inbox, delineated by topic, to a directory for
        # a container to mount; returns a list of created inboxes
        container_inboxes = self.inboxer.promote_to_container_inbox(topic, str(uuid4()))

        if container_inboxes is None or len(container_inboxes) == 0:
            print "There are no container inboxes available for the event run; did something weird happen?"
            return None

        for container_inbox in container_inboxes:
            # container_inbox is the path inboxer promoted to be mounted in the docker container
            self.docker_agent.pull(container_name)
            self.docker_agent.start_container(host_inbox=container_inbox, image_name=container_name)

    # Get the current time, in seconds, since epoch
    def __get_current_time_in_seconds(self):
        return timegm(gmtime())

    # This event handler is executed every time a file is put into the master inbox
    # The data argument includes a property specify the topic that was appended to
    def __handle_inbox_received_event(self, data):
        topic = data["topic"]
        count = self.inboxer.get_inbox_count(topic)
        # Get a list of all files in the inbox delineated by the topic in the event
        inbox_list = self.inboxer.get_inbox_list(topic)

        # If there are no items in the inbox then there is literally nothing to do
        if count == 0:
            return None

        container_infos = self.__get_registered_containers(data["topic"])

        # We have no container infos! :(
        if container_infos is None:
            print "Container for topic not found; doing nothing..."
            return None

        for container_info in container_infos:
            container = container_info["container"]
            # If the count has reached the threshold then it's time to execute!
            threshold = container_info["threshold"] if container_info["threshold"] is not None else 1
            if count >= threshold:
                self.__process(topic, container)
            else:
                # We haven't hit the threshold so we need to start counting down
                # Set the current time
                if topic not in self.pending:
                    self.pending[topic] = {}
                self.pending[topic][container] = (self.__get_current_time_in_seconds() + container_info["timeout"])
