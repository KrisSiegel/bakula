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

# pip install itsdangerous
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)

def generate_auth_token(secret, id, expiration_in_seconds=10):
    """Generate a token

    This will use itsdangers to generate a token which consits of the username
    and expiration time in seconds. Right now we don't do any sophisticated
    checking to see if the token is still valid or not.

    Args:
        secret: the site secret used to generate the tokens
        id: the user ID to encode in the token
        expiration_in_seconds: number of seconds before token expires

    Returns:
        a string representing an encrypted dictionary
    """
    s = Serializer(secret, expires_in = expiration_in_seconds)
    return s.dumps({'id' : id})

def verify_token(secret, token):
    """Verify that a token is a valid

    Args:
        secret: the site secret used to generate tokens
        token: the token to verify

    Returns:
        The user ID from the token if its a valid token None otherwise
    """
    if not token:
        return None
    s = Serializer(secret)
    id = None
    try:
        data = s.loads(token)
        id = data['id']
    except SignatureExpired:
        return None
    except BadSignature:
        return None
    return id
