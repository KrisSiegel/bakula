#!/usr/bin/python

import docker
import pprint
import sys
import time

class DockerAgent(object):
    def __init__(self, docker_base_url='unix://var/run/docker.sock',
                 name_dict=None, should_update_dict=False):
        self._docker_client = docker.Client(base_url=docker_base_url)
        self._should_update_name__dict = should_update_dict
        self._containers = {}
        if name_dict:
            self._name_dict = name_dict
        else:
            self._name_dict = {}
            self._update_container_indexes()

    def build_image(self, path, image_name,
                    dockerfile='Dockerfile'):
        build_generator = self._docker_client.build(path=path, tag=image_name)
	for line in build_generator:
		print line

    def check_if_image_exists(self, image_name):
        for image in self._docker_client.images():
            if 'RepoTags' in image and image_name in image['RepoTags']:
                return True
        return False

    def start_container(self, image_name, should_update_index=True, ports=None):
        container_name = self._create_container_name(image_name)
        print image_name
        container = self._docker_client.create_container(image=image_name,
                                                         name=container_name)
        container_id = container['Id']
        res = self._docker_client.start(container['Id'], port_bindings=ports)
        print res
        self._add_name_to_name_dict(image_name, container_name)
        if should_update_index:
            # Make sure our dictionary is fresh
            self._update_container_indexes()
        return container_id

    def stop_container(self, container_name, should_update_index=True):
        container_id = self._containers[container_name]
        self._docker_client.stop(container=container_id, timeout=5)
        time.sleep(5)
        self._docker_client.remove_container(container=container_id, v=True,
                                             force=True)
        if should_update_index:
            self._update_container_indexes()


    def stop_all_containers_of_image(self, image_name, should_update_index=True):
        for container_name in self._name_dict[image_name]:
            self.stop_container(container_name, False)

        if should_update_index:
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
        print image_name
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
        image_name = image_name.replace('/', '_')
        image_name = image_name.replace('-', '_')
        return image_name

    def _add_name_to_name_dict(self, image_name, name):
        if not image_name in self._name_dict:
            self._name_dict[image_name]=[name]
        else:
            self._name_dict[image_name].append(name)

