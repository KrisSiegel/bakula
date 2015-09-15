#!/bin/bash

data="{\"event_type\" : \"accumulo\", \"event_key\" : \"table\", \"other_stuff\" : \"foo\"}"
echo $data
curl -H "Content-Type: application/json" -X POST http://localhost:4242/events --data "$data"
