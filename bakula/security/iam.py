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
from bakula.models import User
from hashlib import md5

def authenticate(id, password):
    """Authenticate the user against the underlying IAM

    Args:
        id: The ID of the user
        password: The password for the user to verify

    Returns:
        a boolean if the user is authenticated to use Bakula
    """
    try:
        User.get(User.id == id, User.password == md5(password).hexdigest())
        return True
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
        User.create(id=id, password=md5(password).hexdigest())
        return True
    except IntegrityError:
        return False