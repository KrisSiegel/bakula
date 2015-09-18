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
import uuid

# This class handles the event handling of the inboxer and, when a threshold is hit,
# it promotes the appropriate files as an inbox or a docker container then fires the
# docker container.
class Orchestrator:
    def __init__(self, inboxer=Inboxer()):
        self.inboxer = inboxer
        self.inboxer.on("received", self.__handle_inbox_received_event)

    # This event handler is executed every time a file is put into the master inbox
    # The data argument includes a property specify the topic that was appended to
    def __handle_inbox_received_event(self, data):
        inbox_list = self.inboxer.get_inbox_list(data["topic"])

        if len(inbox_list) > 1: # This is just a temporary threshold
            container_inboxes = self.inboxer.promote_to_container_inbox(data["topic"], str(uuid.uuid4()))

            for container_inbox in container_inboxes:
                agent = DockerAgent(container_inbox=container_inbox)
                # TODO: DockerAgent creation currently fails; fix and make it start a container
