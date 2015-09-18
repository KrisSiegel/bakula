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
from bakula.models import User
import bcrypt

def authenticate(id, password):
    """Authenticate the user against the underlying IAM

    Args:
        id: The ID of the user
        password: The password for the user to verify

    Returns:
        a boolean if the user is authenticated to use Bakula
    """
    try:
        user = User.get(User.id == id)
        # Check that the incoming (unhashed) password matches the stored (hashed)
        # password. The hashpw method takes the hashed password, uses the stored salt, and
        # hashes the incoming password. Then we check the result against the stored (hashed)
        # password.
        if bcrypt.hashpw(password, user.password) == user.password:
            return True
        return False
    except User.DoesNotExist:
        return False

def create(id, password):
    """Create a new user in the Bakula IAM

    Args:
        id: The new user's ID
        password: The new user's password

    Returns:
        True if created
    """
    try:
        User.get(User.id == id)
        return False
    except User.DoesNotExist:
        User.create(id=id, password=bcrypt.hashpw(password, bcrypt.gensalt()))
        return True