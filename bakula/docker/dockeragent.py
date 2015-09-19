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
import pprint
import sys
import time

class DockerAgent(object):
    CONTAINER_INBOX = '/inbox'
    NAME_CHARS_TO_REPLACE = ['/', '-', ':']

    def __init__(self, docker_base_url='unix://var/run/docker.sock',
                 registry_host=None,
                 username=None,
                 password=None,
                 registry_protocol='https',
                 tls_config=False):

        self._containers = {}
        self._name_dict = {}
        self._docker_client = docker.Client(base_url=docker_base_url, tls=tls_config)
        if registry_host and registry_protocol and username and password:
            registry_url="%s://%s" % (registry_protocol, registry_host)
            self._docker_client.login(username,
                                      password,
                                      registry=registry_url)

        self._update_container_indexes()

    def build_image(self, path, image_name,
                    dockerfile='Dockerfile'):
        build_generator = self._docker_client.build(path=path, tag=image_name)

    def pull(self, repository, tag):
        return self._docker_client.pull(repository, tag=tag)

    def check_if_image_exists(self, image_name):
        for image in self._docker_client.images():
            if 'RepoTags' in image and image_name in image['RepoTags']:
                return True
        return False

    def start_container(self,
                        image_name,
                        host_inbox,
                        ports=None,
                        run_privileged=False,
                        command=None):
        container_name = self._create_container_name(image_name)

        # Create inbox volume for container
        container_volumes_str = '%s:%s:rw' % (host_inbox, DockerAgent.CONTAINER_INBOX)

        host_config_obj = self._docker_client.create_host_config(
            privileged=run_privileged,
            binds=[container_volumes_str],
            port_bindings=ports
        )
        container = self._docker_client.create_container(image=image_name,
                                                         name=container_name,
                                                         host_config=host_config_obj,
                                                         volumes=[DockerAgent.CONTAINER_INBOX],
                                                         command=command)
        container_id = container['Id']
        res = self._docker_client.start(container['Id'])
        # Make sure our dictionary is fresh
        self._update_container_indexes()
        return container_id

    def stop_container(self, container_name):
        container_id = self._containers[container_name]
        self._docker_client.stop(container=container_id, timeout=5)
        time.sleep(5)
        self._docker_client.remove_container(container=container_id, v=True,
                                             force=True)
        self._update_container_indexes()


    def stop_all_containers_of_image(self, image_name):
        for container_name in self._name_dict[image_name]:
            self.stop_container(container_name, False)
        self._update_container_indexes()

    def get_port_info_for_container(self, container_id, port):
        return self._docker_client.port(container_id, port)

    def _update_container_indexes(self):
        self._name_dict = {}
        self._containers = {}
        for container in self._docker_client.containers():
            image_name = container['Image']
            image_name = image_name[0:image_name.rfind(':')]
            # We only believe in one name per container here folks
            name = container['Names'][0]
            # Remove the first /
            name = name[1:]
            self._add_name_to_name_dict(image_name, name)
            self._containers[name] = container['Id']

    def _create_container_name(self, image_name):
        nin = self._normalize_image_name(image_name)
        # New image being inserted
        if image_name not in self._name_dict:
            container_name = '%s_%d' % (nin, 0)
            return container_name

        # Get our candidates
        instance_numbers = []
        for name in self._name_dict[image_name]:
            # Get our instance number
            instance_numbers.append(int(name[name.rindex('_')+1:]))

        container_name = ''
        if len(instance_numbers) < 2:
            container_name = '%s_%d' % (nin, 1)
        else:
            prev_instance = 0
            instance_numbers.sort()
            for instance in instance_numbers:
                if instance - prev_instance > 1:
                    break
                prev_instance = instance
            container_name = '%s_%d' % (nin, prev_instance+1)

        return container_name


    def _normalize_image_name(self, image_name):
        for char in DockerAgent.NAME_CHARS_TO_REPLACE:
            image_name = image_name.replace(char, '_')
        return image_name

    def _add_name_to_name_dict(self, image_name, name):
        if not image_name in self._name_dict:
            self._name_dict[image_name]=[name]
        else:
            self._name_dict[image_name].append(name)

