import dockeragent
import time
import json
import requests

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
    
    def register_image(self, json):
        key = self._get_event_key(json)
        value = []
        if key in self.events_to_images:
            value = self._events_to_images[key]
        value.append(json['image_name'])
        self.events_to_images[key] = value

    def send_event(self, event_json):
        images = self.events_to_images[self._get_event_key(event_json)]
        for image in images:
            container_url = self.get_url_for_image(image)
            # Start a container
            if not container_url:
                container_url = self._start_container(image)
            print "CONTAINER URL: %s" % container_url
            time.sleep(2)
            headers = {'Content-Type' : 'application/json'}
            requests.post(container_url, data=json.dumps(event_json), headers=headers)
    
    def _get_event_key(self, event_json):
        return "%s_%s" % (event_json['event_type'], event_json['event_key'])
    
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
