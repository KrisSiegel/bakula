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

import inspect
from bottle import HTTPResponse, request
from bakula.security import tokenutils

class TokenAuthorizationPlugin(object):
    """This plugin will verify that a http request has a valid token.
        Attributes:
            secret : the site secret used to verify tokens
    """
    name = 'token_authorization'
    api  = 2

    def __init__(self, secret):
        self.secret = secret

    def apply(self, callback, route):
        """The decorator for the plugin it will
        This will also inject token into the keyword arguments so that the user
        can get to the token. It will be the keyword 'token'.
        Args:
            callback: the function to call if we have a verified token
            route: the route that we are decorating
        Returns:
            the return value of the callback or a HTTPResponse with a 401
            status code and a Bad Token message
        """
        def wrapper(*args, **kwargs):
            token = request.get_header('Authorization', None)
            username = tokenutils.verify_token(self.secret, token)
            if not username:
                rv = HTTPResponse('Bad Token', 401)
            else:
                route_args = inspect.getargspec(route.callback)[0]
                if 'user' in route_args:
                    kwargs['user'] = username
                if 'token' in route_args:
                    kwargs['token'] = token
                rv = callback(*args, **kwargs)
            return rv
        return wrapper