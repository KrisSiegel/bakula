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

import docker
import time
import threading
from sets import Set
import copy

# The requests library seems to import the urllib library completely
# into their codebase before distributing (not sure if it's a fork or
# what), which is why this exceptions module is imported weirdly.
from requests.packages.urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ReadTimeout

class ContainerStartException(Exception):
    pass

class DockerAgent(object):
    CONTAINER_INBOX = '/inbox'
    NAME_CHARS_TO_REPLACE = ['/', '-', ':']

    def __init__(self, docker_base_url='unix://var/run/docker.sock',
                 registry_host=None,
                 username=None,
                 password=None,
                 registry_protocol='https',
                 tls_config=False,
                 monitor_interval=2,
                 docker_timeout=2,
                 monitor_thread=True,
                 start_retries=3):
        self._start_retries = start_retries
        self._containers_to_remove = Set()
        self._terminate_callbacks = {}
        self._docker_client = docker.Client(base_url=docker_base_url,
                                            tls=tls_config,
                                            timeout=docker_timeout)
        if registry_host and registry_protocol and username and password:
            registry_url = "%s://%s" % (registry_protocol, registry_host)
            self._docker_client.login(username,
                                      password,
                                      registry=registry_url)

        self._monitor_thread = None
        if monitor_thread:
            self._monitor_interval = monitor_interval
            self._monitor_thread = threading.Thread(target=self.__monitor)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()

            self._removal_thread = threading.Thread(target=self.__remove)
            self._removal_thread.daemon = True
            self._removal_thread.start()

    def __remove(self):
        while True:
            try:
                time.sleep(self._monitor_interval)
            except KeyboardInterrupt:
                self._removal_thread.stop()
            to_clear = []

            # Make a deep copy of the containers_to_remove so that we can
            # iterate over the containers without blocking the monitor thread
            removing = copy.deepcopy(self._containers_to_remove)
            for container_id in removing:
                try:
                    self._docker_client.remove_container(container_id)
                    to_clear.append(container_id)
                except:
                    # If there's a timeout just bail out of the loop
                    # and we'll remove the containers on the next run
                    break
            for container_id in to_clear:
                self._containers_to_remove.remove(container_id)

    def __monitor(self):
        while True:
            try:
                time.sleep(self._monitor_interval)
            except KeyboardInterrupt:
                self._monitor_thread.stop()
            try:
                exited = self._docker_client.containers(
                    filters={'status': 'exited'}
                )
                update_indices = False
                containers_to_remove = []
                for container in exited:
                    image = container['Image']
                    name = container['Names'][0]
                    container_id = container['Id']
                    if name.startswith('/'):
                        name = name[1:]
                    update_indices = True
                    if container_id in self._terminate_callbacks:
                        self._terminate_callbacks[container_id](container_id)
                        del self._terminate_callbacks[container_id]
                    self._containers_to_remove.add(container_id)
            except:
                # Not too worried about if there is an exception, just want
                # to make sure this thread stays alive
                pass

    def build_image(self, path, image_name,
                    dockerfile='Dockerfile'):
        build_generator = self._docker_client.build(path=path, tag=image_name)

    def pull(self, image_name, tag='latest'):
        return self._docker_client.pull(image_name, tag=tag)

    def check_if_image_exists(self, image_name):
        for image in self._docker_client.images():
            repo_tags = image.get('RepoTags', [])
            if any(image_name in x for x in repo_tags):
                return True
            if 'RepoTags' in image and image_name in image['RepoTags']:
                return True
        return False

    def __process_stats(self,
                       container_id,
                       topic,
                       container_name,
                       stat_generator,
                       stat_processor):
        try:
            for stat in stat_generator:
                stat_processor(stat, container_id, topic, container_name)
        except ReadTimeoutError:
            # When the container is terminated, the connection stays open
            # briefly before timing out. Nothing to do here.
            pass

    def stats(self,
              container_id,
              topic,
              container_name,
              stat_processor):
        stats = self._docker_client.stats(container_id, decode=True)
        thread = threading.Thread(
            target=self.__process_stats,
            args=(container_id, topic, container_name, stats, stat_processor)
        )
        thread.daemon = True
        thread.start()

    def start_container(self,
                        image_name,
                        host_inbox,
                        ports=None,
                        run_privileged=False,
                        command=None,
                        on_terminate=None,
                        topic=None):
        # Create inbox volume for container
        container_volumes_str = '%s:%s:rw' % (host_inbox,
                                              DockerAgent.CONTAINER_INBOX)

        host_config_obj = self._docker_client.create_host_config(
            privileged=run_privileged,
            binds=[container_volumes_str],
            port_bindings=ports
        )
        tries = 0
        created = False
        container = None
        while tries < self._start_retries:
            try:
                container = self._docker_client.create_container(
                    image=image_name,
                    host_config=host_config_obj,
                    volumes=[DockerAgent.CONTAINER_INBOX],
                    command=command,
                    labels={
                        'topic': topic
                    }
                )
                created = True
                break
            except ReadTimeout:
                tries += 1
        if not created:
            raise ContainerStartException('Could not create container')
        container_id = container['Id']
        tries = 0
        while tries < self._start_retries:
            try:
                res = self._docker_client.start(container['Id'])
                if on_terminate is not None:
                    self._terminate_callbacks[container_id] = on_terminate
                return container_id
            except ReadTimeout:
                tries += 1

        # We weren't able to start the container, remove it and throw an
        # error
        self._containers_to_remove.add(container_id)
        raise ContainerStartException('Could not start container "%s%' % container_id)

    def container_count(self, topic, image_name):
        containers = self._docker_client.containers(filters={
            'label': 'topic=%s' % topic,
        })
        count = 0
        for container in containers:
            container_image = container['Image']
            if container_image.startswith(image_name):
                count += 1
        return count
