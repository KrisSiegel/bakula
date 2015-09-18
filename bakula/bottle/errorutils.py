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

from bottle import HTTPResponse, HTTP_CODES
import json

def create_error(status_code=500, message=None, error=None):
    """Simple helper method create a error which matches boomjs

    Args:
        status_code: HTTP status code number (NO sanity check performed)
        error: The error message to send with the code, defaults to HTTP
               standard messages
        message: A detailed error message from the application

    Returns:
        A HTTPResponse object with the body set to a json dump of the message,
        status code, and error. The object also has the proper status code set
        and its content type is application/json.
    """
    if not error:
        error = HTTP_CODES[status_code]

    if not message:
        message = ''

    error_dict = {'statusCode' : status_code,
                  'error'      : error,
                  'message'    : message
                 }

    ret_val = HTTPResponse(status=status_code,
                           headers={'Content-Type' : 'applicaton/json'},
                           body=json.dumps(error_dict))
    return ret_val

def check_missing_json_fields(json_obj, required_fields):
    """Method to validate if a JSON object has the fields that are rquired

    Args:
        json_obj: The json object to check for the required fields
        required_fields: A list of fields to check the JSON object for

    Returns:
        An HTTP error if there are missing fields or None if all the required
        fields are present.
    """
    missing_fields = []
    for required_field in required_fields:
        if required_field not in json_obj:
            missing_fields.append(required_field)

    ret_val = None
    if len(missing_fields) > 0:
        error_msg = ("Payload validation error: The following parameters are",
                     "required but missing %s") % ','.join(missing_fields)
        ret_val = create_error(status=400, message=error_msg)
    return ret_val


