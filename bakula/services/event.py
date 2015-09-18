# Copyright 2015 Immuta, Inc. Licensed under the Immuta Software License
# Version 0.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#
#    http://www.immuta.com/licenses/Immuta_Software_License_0.1.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from bottle import Bottle, HTTPResponse, request, response, FileUpload

from bakula.bottle import configuration
from bakula.bottle.errorutils import create_error
from bakula.events.inboxer import Inboxer
from atomic import AtomicLong

app = Bottle()

configuration.bootstrap_app_config(app)

count = AtomicLong(0)
inbox = Inboxer(atomic_counter=count)

# Accepts a multipart form
# Field 'topic' -> The topic for the attached file(s)
# Field * -> Any field name that is a UploadFile object
@app.post('/event')
def post_event():
    topic = request.forms.get("topic")
    successfully_queued = []
    # Bottle default way of accessing files doesn't seem to like multiple files
    # which use the same form name (which is standard practice). So let's access
    # them manually. Muwhahahahaha.
    for name, item in request.POST.allitems():
        if isinstance(item, FileUpload):
            inbox.add_file_by_bytes(topic, item.file.read())
            successfully_queued.append(item.filename)

    return { "results": successfully_queued }
