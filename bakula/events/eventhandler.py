import time
import json
import requests
import os
import tarfile
import tempfile
import zipfile

from bakula.docker import dockeragent

class EventHandler:
    def __init__(self):
        self._docker_agent = dockeragent.DockerAgent()
        self.events_to_images = {}
        self.image_to_url = {}
        self.port_number = 1233

    def get_registered_images(self):
        return self.events_to_images

    def get_url_for_image(self, image_name):
        if image_name not in self.image_to_url:
            return None
        return self.image_to_url[image_name]

    def register_image(self, event_type, event_key, image_name, path):
        # If our image doesn't exist then build it
        if not self._docker_agent.check_if_image_exists(image_name):
            self._uncompress_file_and_build_image(path, image_name)

        key = self._get_key(event_type, event_key)
        value = []
        if key in self.events_to_images:
            value = self.events_to_images[key]
        value.append(image_name)
        self.events_to_images[key] = value

    def send_event(self, event_json):
        event_type = event_json['event_type']
        event_key = event_json['event_key']
        key = self._get_key(event_type, event_key)
        print key
        if not key in self.events_to_images:
            return
        images = self.events_to_images[key]
        for image in images:
            container_url = self.get_url_for_image(image)
            # Start a container
            if not container_url:
                container_url = self._start_container(image)
            print "CONTAINER URL: %s" % container_url
            time.sleep(2)
            headers = {'Content-Type' : 'application/json'}
            requests.post(container_url, data=json.dumps(event_json), headers=headers)

    def _get_key(self, event_type, event_key):
        return "%s_%s" % (event_type, event_key)

    def _start_container(self, image):
        # Starting container
        self.port_number = self.port_number + 1
        ports = {80: ('0.0.0.0', self.port_number)}
        container_id = self._docker_agent.start_container(image, ports=ports)
        # We assume everything is started on port 80
        info = self._docker_agent.get_port_info_for_container(container_id, 80)
        host_name = info[0]['HostIp']
        host_port = info[0]['HostPort']
        if host_name == '0.0.0.0':
            host_name = '127.0.0.1'
        url = 'http://%s:%s/events' % (host_name, host_port)
        self.image_to_url[image] = url
        return url

    def _uncompress_file_and_build_image(self, path, image_name):
        compressed = None
        file_name, file_extension = os.path.splitext(path)
        if file_extension == '.tar':
            compressed = tarfile.TarFile(name=path)
        elif file_extension =='.zip':
            compressed = zipfile.ZipFile(path)
        else:
            raise RuntimeError("Unrecogonized Extension")

        extraction_site = tempfile.mkdtemp()
        compressed.extractall(path=extraction_site)

        self._docker_agent.build_image(extraction_site, image_name)


