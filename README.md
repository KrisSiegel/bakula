## Bakula

Bakula is a reactive programming platform which allows developers to quickly and
easily build event-driven applications with no strict API to implement. Bakula
events are propagated via registratered 'topics' to user-provided Docker
containers for processing.

Bakula can be used with any Docker Registry (including the Docker Hub) to
pull Docker images and spin up containers for processing events.

### Events

An 'event' in Bakula is any data provided to the service via POSTing to the
```/event``` endpoint. Bakula can process a single event, or multiple events,
in one call to the API. The call to the API must be a ```multipart/form-data```
request, with a payload containing a 'topic' field along with one or more
fields containing files. Each file uploaded to the ```/event``` endpoint is
an individual event object passed to all registered containers.

An event object can be absolutely anything. These event objects are passed directly
to the containers for processing. Two common patterns for events are:

* Claim Check: The event is simply a notification that something has occurred with
some metadata. For example, a database change has taken place, so the event has
the table name, affected ID, and action that has taken place. A container can then
inspect the event, connect to the database and take the appropriate action.
* Data Passing: The event is a full piece of affected data. For example, a stream
of Twitter data is passed directly to Bakula and disseminated across the associated
containers for processing. Each container receives full tweet JSON documents.

Events are provided to each container in the ```/inbox``` directory on the
container. The filenames for each event are simply unique numbers.

### Registrations

When events enter the system, Bakula uses registrations to determine which containers
should be run, and when. Each Bakula registration contains the following:

* Topic: A topic is simply a string that identifies a type of event. For example a
stream of twitter data may be sent to the 'Twitter' topic.
* Container: The full name of the Docker image to be pulled and started as a container
when events occur for this topic.
* Threshold (optional): The number of events which must occur before a container is
started. For example, a threshold of 1000 would denote that 1000 events must occur before
a container is started for this registration.
* Timeout (required with threshold): If events begin to occur, but the threshold is
not met, a countdown will start and a container will be spun up at the end of that
timeout. This prevents data from sitting in Bakula unprocessed. Timeouts are in seconds.
* Privileged (false by default): Dangerous setting. This denotes that containers for
this registration are run in privileged mode, allowing access to the host machine's
devices. Read more about privileged mode [here](http://blog.docker.com/2013/09/docker-can-now-run-within-docker/).

Registrations are created through the Bakula UI.

### Security

Bakula maintains an internal database of users, bootstrapped by an Admin user. The
admin user has the ability to create additional users, and only authenticated users may
perform actions on the system (creating registrations, publishing events, etc.).

API calls are made with a token retrieved after the user logs in via the ```/login```
endpoint. Communication with Bakula should be secured behind SSL.

## Development

### Testing

All test files in Bakula should be written with unittest, and should live
inside *_test.py files in the same directory as the unit under test. To run
all unit tests, execute the following command (this will install nose as
a test dependency):

```bash
python setup.py test
```

### Formatting

To check the formatting of all code against PEP8, run the following command:

```bash
python setup.py pep8
```

## License

Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
